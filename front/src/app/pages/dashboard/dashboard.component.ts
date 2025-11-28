import {
  Component,
  ElementRef,
  AfterViewInit,
  Renderer2,
  HostListener,
  ChangeDetectionStrategy,
} from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent implements AfterViewInit {
  activeIndex = 0;
  isLoggedIn = false;

  /** Modals */
  showProfile = false;
  showLogin = false;
  showSignup = false;

  /**Navigation Items */
  navItems = [
    { name: 'Home', target: 'hero', icon: 'pi-home' },
    { name: 'Create', target: 'create', icon: 'pi-plus' },
    { name: 'History', target: 'history', icon: 'pi-history' },
    { name: 'Discover', target: 'discover', icon: 'pi-compass' },
    { name: 'Profile', target: '', icon: 'pi-user' },
    { name: 'Settings', target: '', icon: 'pi-cog' },
  ];

  /** Cached references */
  private tabs!: NodeListOf<HTMLElement>;
  private indicator!: HTMLElement;
  private navContainer!: HTMLElement;
  private sectionOffsets: { id: string; top: number }[] = [];

  private isClickScrolling = false;
  private scrollPending = false;

  constructor(private el: ElementRef, private renderer: Renderer2) {}

  ngAfterViewInit() {
    // cache elements
    this.tabs = this.el.nativeElement.querySelectorAll('.nav-item');
    this.indicator = this.el.nativeElement.querySelector('.nav-indicator');
    this.navContainer = this.el.nativeElement.querySelector('.nav-container');

    // initial indicator + offsets
    this.updateIndicatorPosition();
    setTimeout(() => this.calculateSectionOffsets(), 200);

    this.updateScrollLock();
  }

  /** Calculate offsets only when sections exist */
  private calculateSectionOffsets(): void {
    this.sectionOffsets = this.navItems
      .filter((item) => item.target)
      .map((item) => {
        const section = document.getElementById(item.target);
        return { id: item.target, top: section?.offsetTop ?? 0 };
      });
  }

  /** Navigate smoothly */
  navigateToSection(sectionId: string, index: number): void {
    const clicked = this.navItems[index];
    if (clicked.name === 'Profile') {
      this.toggleProfile();
      return;
    }

    this.setActive(index);
    if (!sectionId) return;

    const section = document.getElementById(sectionId);
    if (!section) return;

    this.isClickScrolling = true;

    const yOffset = -10;
    const y = section.getBoundingClientRect().top + window.scrollY + yOffset;
    window.scrollTo({ top: y, behavior: 'smooth' });

    // unlock scroll tracking after a short delay
    setTimeout(() => (this.isClickScrolling = false), 600);
  }

  /** Update active indicator */
  private updateIndicatorPosition(): void {
    if (!this.indicator || !this.tabs?.length || !this.navContainer) return;

    const activeTab = this.tabs[this.activeIndex];
    const tabRect = activeTab.getBoundingClientRect();
    const containerRect = this.navContainer.getBoundingClientRect();
    const centerY = tabRect.top - containerRect.top + tabRect.height / 2;

    const indicatorHeight = this.indicator.offsetHeight;
    const finalTop = centerY - indicatorHeight / 2;

    // Apply via Renderer for Angular safety
    this.renderer.setStyle(
      this.indicator,
      'transition',
      'top 0.35s cubic-bezier(0.23, 1, 0.32, 1), background 0.3s ease'
    );
    this.renderer.setStyle(this.indicator, 'top', `${finalTop}px`);

    const colors = ['#e18e1c', '#e3911a', '#e1921a', '#e39519', '#e2921a', '#e3911a'];
    this.renderer.setStyle(
      this.indicator,
      'background',
      colors[this.activeIndex % colors.length]
    );
  }

  /** Scroll tracking (throttled with rAF) */
  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    if (this.isClickScrolling || !this.isLoggedIn) return;
    if (this.scrollPending) return;

    this.scrollPending = true;
    requestAnimationFrame(() => {
      this.handleScroll();
      this.scrollPending = false;
    });
  }

  private handleScroll(): void {
    const scrollY = window.scrollY + window.innerHeight / 3;

    for (let i = this.sectionOffsets.length - 1; i >= 0; i--) {
      if (scrollY >= this.sectionOffsets[i].top) {
        if (this.activeIndex !== i) {
          this.activeIndex = i;
          this.updateIndicatorPosition();
        }
        break;
      }
    }
  }

  /** Resize observer for offsets */
  @HostListener('window:resize', [])
  onResize() {
    this.calculateSectionOffsets();
  }

  /** Modal control */
  toggleProfile() {
    this.showProfile = !this.showProfile;
  }
  closeProfile() {
    this.showProfile = false;
  }

  toggleLogin() {
    this.showLogin = !this.showLogin;
  }
  closeLogin() {
    this.showLogin = false;
    this.isLoggedIn = true;
    this.updateScrollLock();
  }

  toggleSignup() {
    this.showSignup = !this.showSignup;
  }
  closeSignup() {
    this.showSignup = false;
    this.isLoggedIn = true;
    this.updateScrollLock();
  }

  /** Lock/unlock scroll */
/** Lock/unlock scroll */
private updateScrollLock() {
  const body = document.body;

  if (!this.isLoggedIn) {
    this.renderer.setStyle(body, 'overflow', 'hidden');
  } else {
    this.renderer.removeStyle(body, 'overflow');
    // Wait for DOM to render sections, then recalc
    setTimeout(() => {
      this.calculateSectionOffsets();
      this.updateIndicatorPosition();
    }, 300);
  }
}



  /** Logout */
  handleLogout() {
    this.isLoggedIn = false;
    this.closeProfile();
    this.updateScrollLock();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /** Hover leave reset */
  onLeave(event: MouseEvent) {
  const container = (event.currentTarget as HTMLElement)
    .closest('.nav-container') as HTMLElement | null;
    
  if (container) {
    container.style.removeProperty('--gel-y');
  }
}


  /** Helpers */
  setActive(index: number): void {
    this.activeIndex = index;
    this.updateIndicatorPosition();
  }
  isActive(index: number): boolean {
    return this.activeIndex === index;
  }
}
