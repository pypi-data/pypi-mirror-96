import svox
import torch
import torch.cuda
import matplotlib.pyplot as plt

device = 'cuda:0'

t = svox.N3Tree.load("/home/sxyu/proj/volrend/build/lego_diffscale.npz",
                      map_location=device)
#  t = svox.N3Tree(map_location=device)
r = svox.VolumeRenderer(t)
#  sqrt_2 = 2 ** -0.5
c2w = torch.tensor([
                [ -0.9999999403953552, 0.0, 0.0, 0.0 ],
                [ 0.0, -0.7341099977493286, 0.6790305972099304, 2.737260103225708 ],
                [ 0.0, 0.6790306568145752, 0.7341098785400391, 2.959291696548462 ],
                [ 0.0, 0.0, 0.0, 1.0 ],
            ], device=device)

#  c2w = torch.tensor([
#                  [
#                      -0.9980270266532898,
#                      -0.0460626520216465,
#                      0.04266570135951042,
#                      0.17199094593524933
#                  ],
#                  [
#                      0.06278638541698456,
#                      -0.7321932911872864,
#                      0.6781967282295227,
#                      2.733898401260376
#                  ],
#                  [
#                      0.0,
#                      0.6795374751091003,
#                      0.7336407899856567,
#                      2.9574005603790283
#                  ],
#                  [
#                      0.0,
#                      0.0,
#                      0.0,
#                      1.0
#                  ]
#              ], device=device)

#  c2w = torch.tensor([[0.0, -sqrt_2, sqrt_2, -1.7],
#                      [-1.0, 0.0,    0.0,     0.0],
#                      [0.0, -sqrt_2, -sqrt_2, 1.7]], device=device)


with torch.no_grad():
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    im = None
    start.record()
    for i in range(5):
        im = r.render_persp(c2w, height=800, width=800, fx=1111, cuda=True, fast=True)
    end.record()

    torch.cuda.synchronize(device)
    dur = start.elapsed_time(end) / 5
    print('render time', dur, 'ms =', 1000 / dur, 'fps')
    print(im.shape)

    im = im.detach().clamp_(0.0, 1.0)
    plt.figure()
    plt.imshow(im.cpu())
    plt.show()
