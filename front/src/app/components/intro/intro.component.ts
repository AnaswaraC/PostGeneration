import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { gsap } from 'gsap';
import { Router } from '@angular/router';

@Component({
  selector: 'app-intro',
  templateUrl: './intro.component.html',
  styleUrls: ['./intro.component.scss']
})
export class IntroComponent implements OnInit {
  @ViewChild('hiveLogo', { static: true }) hiveLogo!: ElementRef;
  @ViewChild('pollynLogo', { static: true }) pollynLogo!: ElementRef;
  @ViewChild('ripple', { static: true }) ripple!: ElementRef;

  animationDone = false;

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.playIntroAnimation();
  }

  private playIntroAnimation(): void {
    const hive = this.hiveLogo.nativeElement;
    const pollyn = this.pollynLogo.nativeElement;
    const ripple = this.ripple.nativeElement;

    const tl = gsap.timeline({ defaults: { ease: 'power3.inOut' } });

    tl
      // 🐝 Hive logo entrance
      .fromTo(hive, { y: '80%', opacity: 0, scale: 0.95 }, {
        y: '0%', opacity: 1, scale: 1, duration: 1, ease: 'power4.out'
      })
      // Subtle pulse
      .to(hive, {
        scale: 1.04, duration: 0.6, yoyo: true, repeat: 1, ease: 'sine.inOut'
      }, '+=0.1')
      // Ripple behind Hive
      .to(ripple, {
        opacity: 0.8, scale: 1.3, duration: 0.8, ease: 'expo.out'
      }, '-=0.4')
      // Hive dissolves
      .to(hive, {
        filter: 'blur(25px)', opacity: 0, scale: 1.05, duration: 1, ease: 'power2.inOut'
      }, '-=0.5')
      // Ripple contracts
      .to(ripple, {
        scale: 0.35, opacity: 0.5, duration: 0.8, ease: 'expo.inOut'
      })
      // 🌸 Pollyn forms
      .fromTo(pollyn, {
        opacity: 0, scale: 0.85, filter: 'blur(12px)'
      }, {
        opacity: 1, scale: 1, filter: 'blur(0)', duration: 1, ease: 'expo.out'
      })
      // Shimmer pulse
      .to(pollyn, {
        scale: 1.03, duration: 0.6, yoyo: true, repeat: 1, ease: 'sine.inOut'
      }, '+=0.4')
      // Glow dissolve + ripple pulse
      .to(pollyn, {
        opacity: 1,
        scale: 1.05,
        filter: 'blur(30px) brightness(1.6)',
        duration: 1,
        ease: 'power2.inOut',
        onStart: () => {
          gsap.to(ripple, {
            opacity: 0.9, scale: 1.6, duration: 1, ease: 'sine.inOut'
          });
        }
      })
      // Fade out Pollyn & ripple
      .to(pollyn, {
        opacity: 0,
        duration: 0.4,
        ease: 'power1.inOut',
        delay: -0.3,
        onComplete: () => this.handleAnimationEnd(ripple)
      });
  }

  private handleAnimationEnd(ripple: HTMLElement): void {
    gsap.to(ripple, { opacity: 0, duration: 0.6, ease: 'sine.inOut' });
    this.animationDone = true;

    // Navigate after short pause
    setTimeout(() => this.router.navigate(['/sequence']), 300);
  }
}
