
# TODO: Write an pipeline with image classification and explanation using GradCAM

# Enable gradient tracking on the input tensor
# This consumes additional memory and computation, but it's necessary for GradCAM, since it requires gradients with respect to the input
# img_tensor.requires_grad_()