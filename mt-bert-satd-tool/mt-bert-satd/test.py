import torch
print(torch.cuda.device_count())  # Number of available GPUs
for i in range(torch.cuda.device_count()):
    print(f"GPU {i}: {torch.cuda.get_device_name(i)}")

torch.cuda.set_device(0)  # Ensure you use device 0 (the only available GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)  # Should print "cuda:0" if GPU is available

import os
print(os.environ.get("CUDA_VISIBLE_DEVICES"))  # Should return None or "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import os
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

