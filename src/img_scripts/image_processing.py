import os
import sys
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms as T

#------------------MODELO U-NET-------------------------------------------
class Conv_3Kernel(nn.Module):
    # Clase para definir convolución con kernel de 3x3
    def __init__(self, input, output):
        super().__init__()
        self.conv1 = nn.Conv2d(input, output, kernel_size=3, stride=1, padding=1)

    def forward(self, x):
        return self.conv1(x)

class Double_Layer_Conv(nn.Module):
    # Bloque de doble convolución para U-Net
    def __init__(self, input, output):
        super().__init__()
        self.double_conv = nn.Sequential(
            Conv_3Kernel(input, output),
            nn.BatchNorm2d(output),
            nn.ReLU(),
            Conv_3Kernel(output, output),
            nn.BatchNorm2d(output),
            nn.ReLU()
        )
    
    def forward(self, x):
        return self.double_conv(x)

class Down_Conv(nn.Module):
    # Proceso de downsample
    def __init__(self, input, output):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.MaxPool2d(2, 2),
            Double_Layer_Conv(input, output)
        )
    
    def forward(self, x):
        return self.encoder(x)

class Up_Conv(nn.Module):
    # Proceso de upconv para el upsample
    def __init__(self, input, output):
        super().__init__()
        self.upsample = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='bicubic'),
            nn.Conv2d(input, int(input / 2), kernel_size=1, stride=1)
        )
        self.decoder = Double_Layer_Conv(input, output)

    def forward(self, x1, x2):
        x1 = self.upsample(x1)
        x = torch.cat([x2, x1], dim=1)
        return self.decoder(x)

class U_NET(nn.Module):
    # Modelo U-Net
    def __init__(self, input, canales, num_classes):
        super().__init__()
        self.first_conv = Double_Layer_Conv(input, canales)
        self.down1 = Down_Conv(canales, 2 * canales)
        self.down2 = Down_Conv(2 * canales, 4 * canales)
        self.down3 = Down_Conv(4 * canales, 8 * canales)
        self.down4 = Down_Conv(8 * canales, 16 * canales)
        self.up1 = Up_Conv(16 * canales, 8 * canales)
        self.up2 = Up_Conv(8 * canales, 4 * canales)
        self.up3 = Up_Conv(4 * canales, 2 * canales)
        self.up4 = Up_Conv(2 * canales, canales)
        self.last = nn.Conv2d(canales, num_classes, kernel_size=1, stride=1)

    def forward(self, x):
        d1 = self.first_conv(x)
        d2 = self.down1(d1)
        d3 = self.down2(d2)
        d4 = self.down3(d3)
        d5 = self.down4(d4)
        up6 = self.up1(d5, d4)
        up7 = self.up2(up6, d3)
        up8 = self.up3(up7, d2)
        up9 = self.up4(up8, d1)
        salida = self.last(up9)
        return salida
#------------------ FIN DEL MODELO U-NET--------------------------------

# Cargar el modelo de PyTorch
model = U_NET(1, 4, 2)
model.load_state_dict(torch.load(sys.argv[2]))
model.eval()

# Función para preprocesar la imagen usando transformaciones de PyTorch
def preprocess_image(image_path):
    image = Image.open(image_path).convert('L')
    transform = T.Compose([T.Resize([224, 224]), T.ToTensor()])
    image_tensor = transform(image).unsqueeze(0)
    return image_tensor

# Función para guardar la imagen original en formato PNG
def save_original_image_as_png(image_path):
    image = Image.open(image_path)
    output_dir = os.path.dirname(image_path)
    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_original.png"
    output_path = os.path.join(output_dir, output_filename)
    image.save(output_path, 'PNG')
    return output_filename

# Función para realizar la inferencia utilizando el modelo de PyTorch
def perform_inference(image_path):
    image_tensor = preprocess_image(image_path)
    with torch.no_grad():
        result = model(image_tensor)
    return result

# Función para postprocesar los resultados
def postprocess_result(result, image_path):
    result_array = result.squeeze().cpu().numpy()
    if len(result_array.shape) == 3:
        result_array = result_array[0]
    processed_image = Image.fromarray(result_array.astype('uint8') * 255, mode='L')
    output_dir = os.path.dirname(image_path)
    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_processed.png"
    output_path = os.path.join(output_dir, output_filename)
    processed_image.save(output_path, format='PNG')
    return output_path, output_filename

#Función que realiza el procesamiento y devuelve los nombres de los archivos resultantes
def process_image_and_return_paths(image_path):
    result = perform_inference(image_path)
    postprocessed_image_path, postprocessed_image_name = postprocess_result(result, image_path)
    return image_path, postprocessed_image_name

#Main del script
if __name__ == "__main__":
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: La ruta de la imagen '{image_path}' no existe.")
        sys.exit(1)
    
    original_image_name_png = save_original_image_as_png(image_path)
    print(original_image_name_png)
    
    image_path, postprocessed_image_path = process_image_and_return_paths(image_path)
    print(image_path)
    print(postprocessed_image_path)
