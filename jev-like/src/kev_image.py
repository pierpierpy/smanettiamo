import torch
import torch.nn.functional as F
from huggingface_hub import hf_hub_download
from safetensors import safe_open
from transformers import AutoConfig, AutoImageProcessor
from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5VisionModel

from kev.api import SystemOneRequest, to_record
from kev.model import rows_of


class KevImage:
    def __init__(self, ck, tok, model, device="mps"):
        self.ck, self.tok, self.model, self.device = ck, tok, model, device
        base = self.ck.meta.base
        self.cfg = AutoConfig.from_pretrained(base, revision=self.ck.meta.base_revision)
        self.proc = AutoImageProcessor.from_pretrained(base, revision=self.ck.meta.base_revision)

        # vision encoder: only the model.visual.* weights of the base model, no copy of the rest
        self.visual = Qwen3_5VisionModel._from_config(self.cfg.vision_config)
        path = hf_hub_download(base, "model.safetensors-00001-of-00001.safetensors", revision=self.ck.meta.base_revision)
        with safe_open(path, framework="pt") as f:
            sd = {k.removeprefix("model.visual."): f.get_tensor(k) for k in f.keys() if k.startswith("model.visual.")}
        self.visual.load_state_dict(sd, strict=True)
        self.visual.to(device=device, dtype=torch.float32).eval()

        self.embed = self.model.lm.get_input_embeddings()
        self.merge = self.cfg.vision_config.spatial_merge_size

    @torch.no_grad()
    def image_features(self, image):
        x = self.proc(images=[image], return_tensors="pt")
        grid = x["image_grid_thw"].to(self.device)
        out = self.visual(x["pixel_values"].to(self.device, torch.float32), grid_thw=grid)
        return out.pooler_output, grid[0]          # [N, 1024] already projected into the text space

    def _row(self, state_ids, branch_ids, image=None):
        """-> embeddings [L, d] and positions [4, L] (text, t, h, w) of one causal row: state + question."""
        pieces = [("text", state_ids)]
        if image is not None:
            feats, grid = image
            pieces += [("text", [self.cfg.vision_start_token_id]), ("image", (feats, grid)), ("text", [self.cfg.vision_end_token_id])]
        pieces.append(("text", branch_ids))

        embs, pos, cur = [], [], 0
        for kind, x in pieces:
            if kind == "text":
                ids = torch.tensor(x, device=self.device)
                embs.append(self.embed(ids))
                pos.append((torch.arange(len(x), device=self.device) + cur).expand(3, -1))
                cur += len(x)
            else:
                feats, grid = x
                t, h, w = grid[0].item(), grid[1].item() // self.merge, grid[2].item() // self.merge
                T, H, W = torch.meshgrid(torch.arange(t), torch.arange(h), torch.arange(w), indexing="ij")
                pos.append(torch.stack([T, H, W]).reshape(3, -1).to(self.device) + cur)
                embs.append(feats.to(embs[0].dtype))
                cur += max(h, w)
        e, p = torch.cat(embs), torch.cat(pos, 1)
        text_pos = torch.arange(e.shape[0], device=self.device)[None]      # only needed for the causal mask
        return e, torch.cat([text_pos, p])

    @torch.no_grad()
    def probs(self, req, image=None):
        """Like model.probs, but row by row by hand, with the photo (if any) after the state."""
        if not isinstance(req, SystemOneRequest): req = SystemOneRequest(**req)
        rec, meta = to_record(req)
        enc = self.model.encode(self.tok, rec)
        S, _, rows = rows_of(enc)
        img = self.image_features(image) if image is not None else None
        out = {}
        for m, r in zip(meta, rows):
            e, p = self._row(S, r["ids"], img)
            h = self.model.lm(inputs_embeds=e[None], position_ids=p[:, None, :]).last_hidden_state.float()[0]
            start = e.shape[0] - len(r["ids"])
            z = self.model.head(h[start + r["decide"]], h[torch.tensor([start + o for o in r["opts"]], device=self.device)])
            out[m["id"]] = dict(zip(m["keys"], F.softmax(z, -1).cpu().tolist()))
        return out
