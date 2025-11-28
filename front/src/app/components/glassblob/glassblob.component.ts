import { Component, ViewChild, ElementRef, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-glass-blob',
  templateUrl: './glassblob.component.html',
  styleUrls: ['./glassblob.component.scss']
})
export class GlassBlobComponent implements AfterViewInit {
  @ViewChild('orbContainer', { static: true }) orbContainer!: ElementRef;
  
  private isDragging = false;
  private dragX = 0;
  private dragY = 0;

  ngAfterViewInit() {
    this.setupMagneticDrag();
  }

  setupMagneticDrag() {
    const container = this.orbContainer.nativeElement;
    const dashboard = container.closest('.orb-dashboard');
    
    if (!dashboard) return;
    
    dashboard.addEventListener('mousemove', (e: MouseEvent) => {
      if (this.isDragging) return;
      
      const rect = container.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const distanceX = e.clientX - centerX;
      const distanceY = e.clientY - centerY;
      const distance = Math.sqrt(distanceX * distanceX + distanceY * distanceY);
      
      // Magnetic pull radius
      const pullRadius = 200;
      
      if (distance < pullRadius) {
        // Calculate pull strength based on distance (ease-out curve)
        const pullStrength = 1 - Math.pow(distance / pullRadius, 2);
        const maxPull = 25;
        
        this.dragX = distanceX * pullStrength * 0.4;
        this.dragY = distanceY * pullStrength * 0.4;
        
        // Smooth limiting
        this.dragX = Math.max(Math.min(this.dragX, maxPull), -maxPull);
        this.dragY = Math.max(Math.min(this.dragY, maxPull), -maxPull);
        
        container.style.transform = `translate(${this.dragX}px, ${this.dragY}px) scale(1.03)`;
      }
    });
    
    dashboard.addEventListener('mouseleave', () => {
      this.returnToCenter();
    });
    
    // Click and drag functionality
    container.addEventListener('mousedown', (e: MouseEvent) => {
      this.isDragging = true;
      container.style.transition = 'transform 0.15s cubic-bezier(0.23, 1, 0.32, 1)';
    });
    
    document.addEventListener('mousemove', (e: MouseEvent) => {
      if (!this.isDragging) return;
      
      const rect = dashboard.getBoundingClientRect();
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      this.dragX = (e.clientX - rect.left - centerX) * 0.6;
      this.dragY = (e.clientY - rect.top - centerY) * 0.6;
      
      // Elastic drag area with soft limits
      const maxDrag = 100;
      this.dragX = Math.max(Math.min(this.dragX, maxDrag), -maxDrag);
      this.dragY = Math.max(Math.min(this.dragY, maxDrag), -maxDrag);
      
      container.style.transform = `translate(${this.dragX}px, ${this.dragY}px) scale(0.96)`;
    });
    
    document.addEventListener('mouseup', () => {
      if (this.isDragging) {
        this.isDragging = false;
        container.style.transition = 'transform 0.8s cubic-bezier(0.23, 1, 0.32, 1)';
        this.returnToCenter();
      }
    });
  }
  
  returnToCenter() {
    const container = this.orbContainer.nativeElement;
    this.dragX = 0;
    this.dragY = 0;
    container.style.transform = 'translate(0px, 0px) scale(1)';
  }
}