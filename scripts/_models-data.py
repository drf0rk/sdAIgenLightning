## MODEL

model_list = {
    "1. AcornMoarMindBreak by Remphanstar [SD1.5]": [
        {'url': "https://huggingface.co/Remphanstar/Rojos/resolve/main/SD.15-AcornMoarMindBreak.safetensors", 'name': "SD.15-AcornMoarMindBreak.safetensors"}
    ],
    "2. Lustify Inpainting by RandomGulag [SD1.5]": [
        {'url': "https://huggingface.co/RandomGulag/lustifySDXLNSFW_oltINPAINTING/resolve/main/lustifySDXLNSFW_oltINPAINTING.safetensors", 'name': "lustifySDXLNSFW_oltINPAINTING.safetensors"}
    ],
    "3. LazyMix Real Amateur Nudes [SD1.5]": [
        {'url': "https://civitai.com/models/10961/lazymix-real-amateur-nudes?modelVersionId=300972", 'name': "lazymixRealAmateur_v10.safetensors"}
    ],
    "4. Unstable Ink Inpainting [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/188884?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "unstableInk_v10Inpainting.safetensors"}
    ],
    "5. Pornmaster Pro v4 Inpainting [SD1.5]": [
        {'url': "https://civitai.com/models/1031352/pornmaster-pro-full-v4-inpainting", 'name': "pornmasterProFull_v4Inpainting.safetensors"}
    ],
    "6. Real X 2.2 [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/179318?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "realx22_original.safetensors"}
    ],
    "7. D5K6.0 by Remphanstar [SD1.5]": [
        {'url': "https://huggingface.co/Remphanstar/Rojos/resolve/main/D5K6.0.safetensors?download=true", 'name': "D5K6.0.safetensors"}
    ],
    "8. Deliberate Inpainting v2 [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/95864?type=Model&format=SafeTensor&size=pruned&fp=fp16", 'name': "deliberate_v2Inpainting.safetensors"}
    ]
}

## VAE

vae_list = {
    "1. VAE-ft-mse-840000-ema-pruned": [
        {'url': "https://civitai.com/api/download/models/88156?type=Model&format=SafeTensor", 'name': "vae-ft-mse-840000-ema-pruned.safetensors"}
    ],
    "2. vae-ft-ema-560000-pruned": [
        {'url': "https://civitai.com/api/download/models/311162?type=Model&format=SafeTensor", 'name': "vae-ft-ema-560000-pruned.safetensors"}
    ]
}

## CONTROLNET

controlnet_list = {
    "1. Openpose": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_openpose_fp16.yaml"}
    ],
    "2. Canny": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_canny_fp16.yaml"}
    ],
    "3. Depth": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11f1p_sd15_depth_fp16.yaml"}
    ],
    "4. Lineart": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_lineart_fp16.yaml"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15s2_lineart_anime_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15s2_lineart_anime_fp16.yaml"}
    ],
    "5. ip2p": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11e_sd15_ip2p_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11e_sd15_ip2p_fp16.yaml"}
    ],
    "6. Shuffle": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11e_sd15_shuffle_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11e_sd15_shuffle_fp16.yaml"}
    ],
    "7. Inpaint": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_inpaint_fp16.yaml"}
    ],
    "8. MLSD": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_mlsd_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_mlsd_fp16.yaml"}
    ],
    "9. Normalbae": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_normalbae_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_normalbae_fp16.yaml"}
    ],
    "10. Scribble": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_scribble_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_scribble_fp16.yaml"}
    ],
    "11. Seg": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_seg_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_seg_fp16.yaml"}
    ],
    "12. Softedge": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_softedge_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_softedge_fp16.yaml"}
    ],
    "13. Tile": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1e_sd15_tile_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11f1e_sd15_tile_fp16.yaml"}
    ]
}
