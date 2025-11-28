import { Component } from '@angular/core';

interface TemplateItem {
  name: string;
  size: string;
  icon: string;
}

interface PreviewCard {
  title: string;
  description: string;
  caption: string;
}

type TemplateCategory = 'Print' | 'Image' | 'Social Media' | 'Presentation' | 'Document';

@Component({
  selector: 'app-create',
  templateUrl: './create.component.html',
  styleUrls: ['./create.component.scss']
})
export class CreateComponent {
  // ====== Preview Cards ======
  previewCards: PreviewCard[] = [
    {
      title: 'Angular 19 Just Dropped ⚡',
      description: 'Explore zoneless change detection and the new signal-based forms API.',
      caption: 'Check out the new features!'
    },
    {
      title: 'Mastering TypeScript 6 🚀',
      description: 'Type inference just got smarter — refactor for cleaner code.',
      caption: 'TypeScript 6 is amazing!'
    },
    {
      title: 'RxJS + Signals Hybrid 🔁',
      description: 'Combine signals and observables for ultra-reactive Angular apps.',
      caption: 'Reactive programming made easier.'
    }
  ];

  currentCardIndex = 0;
  selectedPostCount = 1;

  nextCard() {
    this.currentCardIndex = (this.currentCardIndex + 1) % this.previewCards.length;
  }

  prevCard() {
    this.currentCardIndex =
      (this.currentCardIndex - 1 + this.previewCards.length) % this.previewCards.length;
  }

  getCardStyle(i: number) {
    const offset = i - this.currentCardIndex;
    const peek = 160;
    const scale = i === this.currentCardIndex ? 1 : 0.9;

    return {
      transform: `
        translateX(${offset * peek}px)
        scale(${scale})
        perspective(800px)
        rotateY(${offset * -6}deg)
      `,
    };
  }

  // ====== Template Category Logic ======
  templates: Record<TemplateCategory, TemplateItem[]> = {
    Print: [
      { name: 'Poster', size: 'Portrait', icon: 'assets/icons/poster.svg' },
      { name: 'Brochure', size: '3-Fold', icon: 'assets/icons/brochure.svg' },
      { name: 'Flyer', size: 'Portrait', icon: 'assets/icons/flyer.svg' },
      { name: 'Certificate', size: 'A4 / Letter', icon: 'assets/icons/certificate.svg' }
    ],
    Image: [
      { name: 'Thumbnail', size: '16:9', icon: 'assets/icons/image.svg' },
      { name: 'Banner', size: '1200x400', icon: 'assets/icons/banner.svg' }
    ],
    'Social Media': [
      { name: 'Instagram Post', size: '1080x1080', icon: 'assets/icons/instagram.svg' },
      { name: 'LinkedIn', size: '1080x1080', icon: 'assets/icons/instagram.svg' },
      { name: 'Story', size: '1080x1920', icon: 'assets/icons/story.svg' }
    ],
    Presentation: [
      { name: 'Slide Deck', size: '16:9', icon: 'assets/icons/presentation.svg' }
    ],
    Document: [
      { name: 'Business Report', size: 'A4', icon: 'assets/icons/document.svg' }
    ]
  };

  // Store the list of categories
  templateCategories: TemplateCategory[] = Object.keys(this.templates) as TemplateCategory[];

  selectedCategory: TemplateCategory = 'Print';
  selectedTemplate = '';
}
