import cv2
import numpy as np

def apply_flip(img, active):
    """Horizontal Flip (Mirroring)."""
    if not active: return img
    return cv2.flip(img, 1)

def apply_perspective_warp(img, strength):
    """Applies random perspective warping to simulate camera tilt."""
    if strength <= 0: return img
    
    h, w = img.shape[:2]
    
    # Calculate warp magnitude (max 10%)
    offset = strength * min(h, w) * 0.1

    # Source points (full image)
    src_pts = np.float32([[0, 0], [w-1, 0], [0, h-1], [w-1, h-1]])
    
    # Destination points (Tilt effect)
    dst_pts = np.float32([
        [offset, offset],
        [w-1-offset, offset],
        [0, h-1],
        [w-1, h-1]
    ])
    
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    
    # Warp with reflection padding
    warped = cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)
    return warped

def apply_crop(img, ratio_mode):
    if ratio_mode == "Original": return img
    h, w = img.shape[:2]
    target_ratio = 1.0
    if ratio_mode == "1:1 (Square)": target_ratio = 1.0
    elif ratio_mode == "4:5 (Portrait)": target_ratio = 4/5
    elif ratio_mode == "16:9 (Landscape)": target_ratio = 16/9
    elif ratio_mode == "9:16 (Story)": target_ratio = 9/16
    
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        return img[:, start_x:start_x+new_w]
    else:
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        return img[start_y:start_y+new_h, :]

def apply_unsharp_mask(img, strength):
    if strength <= 0: return img
    gaussian_3 = cv2.GaussianBlur(img, (0, 0), 2.0)
    unsharp_image = cv2.addWeighted(img, 1.0 + strength, gaussian_3, -strength, 0)
    return unsharp_image

def apply_chromatic_aberration(img, strength):
    if strength <= 0: return img
    h, w, c = img.shape
    y, x = np.indices((h, w))
    center_y, center_x = h / 2, w / 2
    offset_y, offset_x = y - center_y, x - center_x
    
    scale_r = 1.0 - (strength * 0.015)
    map_x_r = center_x + offset_x * scale_r
    map_y_r = center_y + offset_y * scale_r
    
    scale_b = 1.0 + (strength * 0.015)
    map_x_b = center_x + offset_x * scale_b
    map_y_b = center_y + offset_y * scale_b
    
    r_chan = cv2.remap(img[:,:,0], map_x_r.astype(np.float32), map_y_r.astype(np.float32), cv2.INTER_LINEAR)
    b_chan = cv2.remap(img[:,:,2], map_x_b.astype(np.float32), map_y_b.astype(np.float32), cv2.INTER_LINEAR)
    
    out = img.copy()
    out[:,:,0] = r_chan
    out[:,:,2] = b_chan
    return out

def apply_iso_grain(img, strength):
    if strength <= 0: return img
    img_norm = img.astype(float) / 255.0
    noise_var = (img_norm + 0.01) * (strength * 0.05)
    noise = np.random.normal(0, 1, img.shape) * np.sqrt(noise_var)
    noisy = img_norm + noise
    return np.clip(noisy * 255.0, 0, 255).astype(np.uint8)

def apply_cfa_resampling(img, active):
    if not active: return img
    h, w = img.shape[:2]
    small = cv2.resize(img, (w//2, h//2), interpolation=cv2.INTER_LINEAR)
    back = cv2.resize(small, (w, h), interpolation=cv2.INTER_CUBIC)
    return back

def spectral_grid_injection_v4(img, strength):
    if strength <= 0: return img
    rows, cols = img.shape[:2]
    crow, ccol = rows // 2, cols // 2
    output = np.zeros_like(img)
    
    # Generate high-frequency grid pattern
    freq_grid = np.zeros((rows, cols))
    step = 32
    for r in range(0, rows, step):
        for c in range(0, cols, step):
            freq_grid[r, c] = 1.0

    # Mask low frequencies
    y, x = np.indices((rows, cols))
    dist_from_center = np.sqrt((x - ccol)**2 + (y - crow)**2)
    max_radius = np.sqrt(ccol**2 + crow**2)
    high_pass_mask = np.clip((dist_from_center - (max_radius * 0.3)) / (max_radius * 0.2), 0, 1)
    
    injection_energy = freq_grid * high_pass_mask * (strength * 4000.0)
    
    # Inject into frequency domain per channel
    for i in range(3):
        f = np.fft.fft2(img[:,:,i])
        fshift = np.fft.fftshift(f)
        
        # Add grid energy to magnitude
        mag = np.abs(fshift)
        ang = np.angle(fshift)
        new_mag = mag + injection_energy
        
        # Reconstruct
        fshift_new = new_mag * np.exp(1j * ang)
        img_back = np.fft.ifft2(np.fft.ifftshift(fshift_new))
        output[:,:,i] = np.abs(img_back)
        
    return np.clip(output, 0, 255).astype(np.uint8)

def chroma_smoothing(img, strength):
    if strength <= 0: return img
    yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
    ksize = int(strength * 20) | 1
    if ksize < 3: ksize = 3
    yuv[:,:,1] = cv2.GaussianBlur(yuv[:,:,1], (ksize, ksize), 0)
    yuv[:,:,2] = cv2.GaussianBlur(yuv[:,:,2], (ksize, ksize), 0)
    return cv2.cvtColor(yuv, cv2.COLOR_YCrCb2RGB)

def artificial_plasticity_v4(img, strength):
    if strength <= 0: return img
    d = 9
    sigma_color = strength * 200.0
    sigma_space = strength * 200.0
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)
