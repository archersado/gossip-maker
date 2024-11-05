import os
import json
import asyncio
from utils.request import APIClient

comfy_client = APIClient(os.environ.get("COMFY_ENTRYPOINT"))


def get_comfy_workflow_v2(prompt: str):
  data = {
    "47": {
      "inputs": {
        "model_name": "AnimateLCM_sd15_t2v.ckpt"
      },
      "class_type": "ADE_LoadAnimateDiffModel",
      "_meta": {
        "title": "Load AnimateDiff Model 🎭🅐🅓②"
      }
    },
    "49": {
      "inputs": {
        "motion_model": [
          "47",
          0
        ]
      },
      "class_type": "ADE_ApplyAnimateDiffModelSimple",
      "_meta": {
        "title": "Apply AnimateDiff Model 🎭🅐🅓②"
      }
    },
    "50": {
      "inputs": {
        "beta_schedule": "lcm[100_ots]",
        "model": [
          "64",
          0
        ],
        "m_models": [
          "49",
          0
        ],
        "context_options": [
          "52",
          0
        ]
      },
      "class_type": "ADE_UseEvolvedSampling",
      "_meta": {
        "title": "Use Evolved Sampling 🎭🅐🅓②"
      }
    },
    "51": {
      "inputs": {
        "ckpt_name": "baseAnimeStyle_v10.safetensors"
      },
      "class_type": "CheckpointLoaderSimple",
      "_meta": {
        "title": "Load Checkpoint"
      }
    },
    "52": {
      "inputs": {
        "context_length": 16,
        "context_stride": 1,
        "context_overlap": 4,
        "fuse_method": "pyramid",
        "use_on_equal_length": False,
        "start_percent": 0,
        "guarantee_steps": 1
      },
      "class_type": "ADE_StandardUniformContextOptions",
      "_meta": {
        "title": "Context Options◆Standard Uniform 🎭🅐🅓"
      }
    },
    "56": {
      "inputs": {
        "samples": [
          "58",
          1
        ],
        "vae": [
          "67",
          0
        ]
      },
      "class_type": "VAEDecode",
      "_meta": {
        "title": "VAE Decode"
      }
    },
    "57": {
      "inputs": {
        "frame_rate": 12,
        "loop_count": 0,
        "filename_prefix": "AnimateDiff",
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 20,
        "save_metadata": True,
        "pingpong": False,
        "save_output": True,
        "images": [
          "56",
          0
        ]
      },
      "class_type": "VHS_VideoCombine",
      "_meta": {
        "title": "Video Combine 🎥🅥🅗🅢"
      }
    },
    "58": {
      "inputs": {
        "add_noise": True,
        "noise_seed": 999889999,
        "cfg": 1.8,
        "model": [
          "50",
          0
        ],
        "positive": [
          "62",
          0
        ],
        "negative": [
          "63",
          0
        ],
        "sampler": [
          "59",
          0
        ],
        "sigmas": [
          "60",
          0
        ],
        "latent_image": [
          "61",
          0
        ]
      },
      "class_type": "SamplerCustom",
      "_meta": {
        "title": "SamplerCustom"
      }
    },
    "59": {
      "inputs": {
        "euler_steps": 2,
        "lcm_steps": 2,
        "tweak_sigmas": False,
        "ancestral": 0
      },
      "class_type": "SamplerLCMCycle",
      "_meta": {
        "title": "SamplerLCMCycle"
      }
    },
    "60": {
      "inputs": {
        "steps": 10,
        "denoise": 1,
        "model": [
          "50",
          0
        ]
      },
      "class_type": "LCMScheduler",
      "_meta": {
        "title": "LCMScheduler"
      }
    },
    "61": {
      "inputs": {
        "width": 512,
        "height": 512,
        "batch_size": 120
      },
      "class_type": "EmptyLatentImage",
      "_meta": {
        "title": "Empty Latent Image"
      }
    },
    "62": {
      "inputs": {
        "text": prompt,
        "token_normalization": "mean",
        "weight_interpretation": "A1111",
        "clip": [
          "64",
          1
        ]
      },
      "class_type": "BNK_CLIPTextEncodeAdvanced",
      "_meta": {
        "title": "CLIP Text Encode (Advanced)"
      }
    },
    "63": {
      "inputs": {
        "text": "(nipples:1.5), (worst quality:1.3), unfinished sketch, blurry, normal, mundane, boring, everyday, safe, ordinary, monochrome, greyscale, NSFW, watermark",
        "token_normalization": "mean",
        "weight_interpretation": "A1111",
        "clip": [
          "64",
          1
        ]
      },
      "class_type": "BNK_CLIPTextEncodeAdvanced",
      "_meta": {
        "title": "CLIP Text Encode (Advanced)"
      }
    },
    "64": {
      "inputs": {
        "lora_name": "AnimateLCM_sd15_t2v_lora.safetensors",
        "strength_model": 1,
        "strength_clip": 1,
        "model": [
          "51",
          0
        ],
        "clip": [
          "51",
          1
        ]
      },
      "class_type": "LoraLoader",
      "_meta": {
        "title": "Load LoRA"
      }
    },
    "67": {
      "inputs": {
        "vae_name": "vae-ft-mse-840000-ema-pruned_fp16.safetensors"
      },
      "class_type": "VAELoader",
      "_meta": {
        "title": "Load VAE"
      }
    },
    "68": {
      "inputs": {},
      "class_type": "VAEDecode",
      "_meta": {
        "title": "VAE Decode"
      }
    }
  }
  return data


def get_comfy_workflow_v1(prompt: str):
  data = {
  "3": {
    "inputs": {
      "text": prompt,
      "clip": [
        "37",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "6": {
    "inputs": {
      "text": "(worst quality, low quality: 1.4)",
      "clip": [
        "37",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "seed": 888888888,
      "steps": 8,
      "cfg": 1.4000000000000001,
      "sampler_name": "lcm",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "36",
        0
      ],
      "positive": [
        "3",
        0
      ],
      "negative": [
        "6",
        0
      ],
      "latent_image": [
        "9",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "9": {
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 24
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "10": {
    "inputs": {
      "samples": [
        "7",
        0
      ],
      "vae": [
        "32",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "32": {
    "inputs": {
      "ckpt_name": "v1-5-pruned-emaonly.ckpt"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "35": {
    "inputs": {
      "frame_rate": 8,
      "loop_count": 0,
      "filename_prefix": "AnimateDiff/readme",
      "format": "video/h264-mp4",
      "pix_fmt": "yuv420p",
      "crf": 19,
      "save_metadata": True,
      "pingpong": False,
      "save_output": True,
      "images": [
        "10",
        0
      ]
    },
    "class_type": "VHS_VideoCombine",
    "_meta": {
      "title": "Video Combine 🎥🅥🅗🅢"
    }
  },
  "36": {
    "inputs": {
      "model_name": "AnimateLCM_sd15_t2v.ckpt",
      "beta_schedule": "lcm",
      "model": [
        "37",
        0
      ]
    },
    "class_type": "ADE_AnimateDiffLoaderGen1",
    "_meta": {
      "title": "AnimateDiff Loader 🎭🅐🅓①"
    }
  },
  "37": {
    "inputs": {
      "lora_name": "AnimateLCM_sd15_t2v_lora.safetensors",
      "strength_model": 0.9,
      "strength_clip": 1,
      "model": [
        "32",
        0
      ],
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  }
}
  return data

async def generate_video_material(keywords: str):
  prompt = get_comfy_workflow_v1(keywords)
  data = {
    "client_id": comfy_client.client_id,
    "prompt": prompt
  }
  res = await comfy_client.post("/prompt", data)
  prompt_id = res.get("prompt_id")

  while True:
    task_res = await comfy_client.get(f"/history/{prompt_id}")
    prompt_res = task_res.get(prompt_id)
    if prompt_res != None:
      status = prompt_res.get("status")
      if status != None:
        completed = status.get("completed")
        if completed:
          return prompt_res.get("outputs")

      # 可以添加适当的延迟以避免过于频繁的请求
    await asyncio.sleep(30)  # 等待 5 秒后再次请求



