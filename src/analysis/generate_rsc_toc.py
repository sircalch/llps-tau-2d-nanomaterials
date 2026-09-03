import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_toc_graphic():
    # RSC Soft Matter guidelines: max 8 cm x 4 cm
    w_in = 8.0 / 2.54
    h_in = 4.0 / 2.54
    
    fig = plt.figure(figsize=(w_in, h_in), dpi=600)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 8.0)
    ax.set_ylim(0, 4.0)
    ax.axis('off')
    
    # Background
    ax.add_patch(patches.Rectangle((0, 0), 8.0, 4.0, facecolor='#F8FAFC', edgecolor='none'))
    
    # Panel 1: Spontaneous LLPS & Condensate Hardening (Left: 0.2 to 2.5)
    ax.add_patch(patches.FancyBboxPatch((0.2, 0.4), 2.2, 3.2, boxstyle='round,pad=0.02,rounding_size=0.15', facecolor='#EFF6FF', edgecolor='#93C5FD', lw=0.8))
    ax.text(1.3, 3.25, 'Bulk Tau LLPS', fontsize=6.2, weight='bold', color='#1E3A8A', ha='center')
    
    # Tau Droplet
    drop = patches.Circle((1.3, 1.8), 0.85, facecolor='#BFDBFE', edgecolor='#2563EB', lw=1.2, alpha=0.9)
    ax.add_patch(drop)
    # Fibril core inside droplet
    np.random.seed(42)
    for _ in range(7):
        x0 = 1.3 + np.random.uniform(-0.40, 0.40)
        y0 = 1.8 + np.random.uniform(-0.40, 0.40)
        dx = np.random.uniform(-0.25, 0.25)
        dy = np.random.uniform(-0.25, 0.25)
        ax.plot([x0, x0+dx], [y0, y0+dy], color='#DC2626', lw=1.3, solid_capstyle='round')
    ax.text(1.3, 0.60, 'Aging & Fibrillation', fontsize=4.8, weight='bold', color='#DC2626', ha='center')
    
    # Panel 2: 2D Nanomaterial Biointerface (Middle: 2.7 to 5.1)
    ax.add_patch(patches.FancyBboxPatch((2.7, 0.4), 2.3, 3.2, boxstyle='round,pad=0.02,rounding_size=0.15', facecolor='#F1F5F9', edgecolor='#CBD5E1', lw=0.8))
    ax.text(3.85, 3.25, '2D Biointerface (as)', fontsize=6.2, weight='bold', color='#334155', ha='center')
    
    # Nanosheet representation (angled parallelogram)
    sheet = patches.Polygon([[3.1, 1.4], [4.4, 1.1], [4.6, 2.5], [3.3, 2.8]], 
                            facecolor='#94A3B8', edgecolor='#475569', lw=1.2, alpha=0.85)
    ax.add_patch(sheet)
    # Adsorbed protein monomers on sheet
    ad_pts = [[3.4, 2.4], [3.8, 2.1], [4.2, 1.8], [4.2, 2.4], [3.5, 1.7]]
    for px, py in ad_pts:
        ax.add_patch(patches.Circle((px, py), 0.09, facecolor='#2563EB', edgecolor='#1D4ED8', lw=0.6))
    
    # Sequestration arrows
    ax.annotate('', xy=(3.6, 1.9), xytext=(2.2, 1.9),
                arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.1, connectionstyle='arc3,rad=-0.15'))
    ax.text(3.85, 0.60, 'Monomer Sequestration', fontsize=4.8, weight='bold', color='#2563EB', ha='center')
    
    # Panel 3: Suppression & Fibrillation Arrest (Right: 5.4 to 7.8)
    ax.add_patch(patches.FancyBboxPatch((5.4, 0.4), 2.3, 3.2, boxstyle='round,pad=0.02,rounding_size=0.15', facecolor='#ECFDF5', edgecolor='#A7F3D0', lw=0.8))
    ax.text(6.55, 3.25, 'LLPS Dissolution', fontsize=6.2, weight='bold', color='#065F46', ha='center')
    
    # Free monomers in dilute solution (no droplet)
    for _ in range(14):
        mx = 5.6 + np.random.uniform(0.1, 1.9)
        my = 1.0 + np.random.uniform(0.1, 1.8)
        ax.add_patch(patches.Circle((mx, my), 0.07, facecolor='#3B82F6', edgecolor='#1D4ED8', lw=0.5, alpha=0.7))
    
    ax.text(6.55, 1.85, 'Droplets Dissolved', fontsize=6.2, weight='bold', color='#059669', ha='center')
    ax.text(6.55, 1.45, 'Aging Retarded', fontsize=5.8, weight='bold', color='#059669', ha='center')
    ax.text(6.55, 0.60, 'Tcloud shifts to 29.4 °C', fontsize=4.8, weight='bold', color='#047857', ha='center')
    
    # Connecting transition arrow
    ax.annotate('', xy=(5.4, 1.9), xytext=(5.05, 1.9),
                arrowprops=dict(arrowstyle='->', color='#0F172A', lw=1.4))
                
    os.makedirs('figures', exist_ok=True)
    out_base = 'figures/TOC_Graphic_RSC_Soft_Matter'
    fig.savefig(f'{out_base}.png', dpi=600)
    fig.savefig(f'{out_base}.pdf')
    fig.savefig(f'{out_base}.tif', dpi=600)
    print(f'RSC TOC Graphic saved: {out_base}.png (.pdf, .tif) [8 cm x 4 cm, 600 dpi]')
    plt.close()

if __name__ == '__main__':
    generate_toc_graphic()
