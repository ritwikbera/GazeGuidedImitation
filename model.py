import torch.nn as nn
from graphLayer import GCU
import torch


class GazePred(nn.Module):

    def __init__(self): # sample batch BCHW
        super(GazePred, self).__init__()
        self.layers_set = False

    def set_layers(self, sample_batch):
        self.conv1 = nn.Conv2d(in_channels=sample_batch.size(1), out_channels=16, kernel_size=8, stride=4, padding=2)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=4, stride=2, padding=1)
        
        self.gc3 = GCU(V=8, batch=sample_batch.size(0))

        gcu_out_ch = 1
        output_dim = 2
        height, width = self.set_hw(sample_batch[0])

        self.conv = nn.Conv2d(in_channels=gcu_out_ch, out_channels=output_dim, kernel_size=3, padding=(1,1))
        self.conv_fc1 = nn.Conv2d(in_channels=height, out_channels=1, kernel_size=1) 
        self.conv_fc2 = nn.Conv2d(in_channels=width, out_channels=1, kernel_size=1)

    def set_hw(self, sample_input):
        return sample_input.size()[-2], sample_input.size()[-1]
      
    def forward(self, x):
        if not self.layers_set:
            self.set_layers(x)

        y = self.gc3(x)
        y = self.conv(y)
        # FC layers fully replaced by  2 fully conv layers
        y = self.conv_fc2(self.conv_fc1(y.permute(0,2,1,3)).permute(0,3,1,2))
        y = y.view(y.size()[0],-1)
        return y

if __name__=='__main__':
    img = torch.randn(1,3,16,16)
    model = GazePred()
    out = model(img)
    print(out.size())