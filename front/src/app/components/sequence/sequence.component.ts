import {
  Component,
  ElementRef,
  AfterViewInit,
  ViewChild,
  ViewChildren,
  QueryList,
  OnDestroy,
  NgZone,
} from '@angular/core';
import { Router } from '@angular/router';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

@Component({
  selector: 'app-sequence',
  templateUrl: './sequence.component.html',
  styleUrls: ['./sequence.component.scss'],
})
export class SequenceComponent implements AfterViewInit, OnDestroy {
  @ViewChild('track', { static: true }) track!: ElementRef<HTMLDivElement>;
  @ViewChild('container', { static: true }) container!: ElementRef<HTMLDivElement>;
  @ViewChildren('slide') slides!: QueryList<ElementRef<HTMLDivElement>>;

  private triggers: ScrollTrigger[] = [];

  constructor(private router: Router, private zone: NgZone) {}

  ngAfterViewInit(): void {
    this.zone.runOutsideAngular(() => {
      requestAnimationFrame(() => this.initAnimations());
      this.slides.changes.subscribe(() =>
        requestAnimationFrame(() => this.initAnimations())
      );
    });
  }

  ngOnDestroy(): void {
    this.clearTriggers();
    gsap.globalTimeline.clear();
  }

  /** Sets up horizontal scroll and per-slide animations */
  private initAnimations(): void {
    this.clearTriggers();

    const track = this.track.nativeElement;
    const container = this.container.nativeElement;
    const slides = this.slides.toArray();
    if (!slides.length) return;

    const containerWidth = container.offsetWidth;
    track.style.width = `${slides.length * 100.2}vw`;

    // Hide all slides except the first
    slides.forEach((slide, i) => this.setSlideInitialState(slide, i === 0));

    // Horizontal scroll tween
    const trackAnim = gsap.to(track, {
      x: () => -(track.scrollWidth - containerWidth),
      ease: 'none',
    });

    // Main scroll trigger controller
    this.triggers.push(
      ScrollTrigger.create({
        animation: trackAnim,
        trigger: container,
        start: 'top top',
        end: () => `+=${track.scrollWidth - containerWidth}`,
        scrub: 0.7,
        pin: true,
        anticipatePin: 1,
        invalidateOnRefresh: true,
        snap: {
          snapTo: (p: number) => gsap.utils.snap(
            slides.map((_, i) => i / (slides.length - 1)),
            p
          ),
          duration: { min: 0.2, max: 0.6 },
          ease: 'power3.inOut',
        },
      })
    );

    // Animate slides on enter
    slides.forEach((slide, i) => {
      if (i > 0) this.createSlideTrigger(slide.nativeElement, trackAnim);
    });

    // Final slide "end" button reveal
    const lastSlide = slides[slides.length - 1].nativeElement;
    const endBtn = lastSlide.querySelector('.end-btn');
    if (endBtn) this.createEndButtonTrigger(lastSlide, endBtn, trackAnim);

    setTimeout(() => ScrollTrigger.refresh(), 120);
  }

  /** Prepares each slide’s initial visibility */
  private setSlideInitialState(slideRef: ElementRef, isVisible: boolean): void {
    const el = slideRef.nativeElement;
    const elements = this.getSlideElements(el);
    gsap.set(elements, { opacity: isVisible ? 1 : 0, y: isVisible ? 0 : 40 });
  }

  /** Creates a ScrollTrigger for each slide’s content */
  private createSlideTrigger(slide: HTMLElement, trackAnim: GSAPTween): void {
    const elements = this.getSlideElements(slide);
    if (!elements.length) return;

    this.triggers.push(
      ScrollTrigger.create({
        trigger: slide,
        containerAnimation: trackAnim,
        start: 'center center',
        onEnter: () =>
          gsap.to(elements, {
            opacity: 1,
            y: 0,
            stagger: 0.15,
            duration: 1,
            ease: 'power3.out',
            overwrite: 'auto',
          }),
      })
    );
  }

  /** Triggers the final “End” button fade-in */
  private createEndButtonTrigger(
    lastSlide: HTMLElement,
    button: Element,
    trackAnim: GSAPTween
  ): void {
    this.triggers.push(
      ScrollTrigger.create({
        trigger: lastSlide,
        containerAnimation: trackAnim,
        start: 'center center',
        onEnter: () =>
          gsap.to(button, {
            opacity: 1,
            duration: 1,
            ease: 'power3.out',
            pointerEvents: 'auto',
          }),
      })
    );
  }

  /** Extracts animatable elements (h1, p, button) */
  private getSlideElements(slide: HTMLElement): Element[] {
    return Array.from(slide.querySelectorAll('h1, p, button'));
  }

  /** Clears all scroll triggers safely */
  private clearTriggers(): void {
    ScrollTrigger.getAll().forEach(t => t.kill());
    this.triggers.forEach(t => t.kill());
    this.triggers = [];
  }

  /** Skip intro button handler */
  skipIntro(): void {
    gsap.to('.intro-sequence', {
      opacity: 0,
      duration: 0.5,
      onComplete: () => {
        this.router.navigate(['/dashboard']).then();
      },
    });
  }
}
