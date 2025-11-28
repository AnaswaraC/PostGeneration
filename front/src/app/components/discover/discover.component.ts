import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

interface DiscoverPost {
  title: string;
  description: string;
  author: string;
  likes: number;
  tags: string[];
  image?: string;
}

@Component({
  selector: 'app-discover',
  templateUrl: './discover.component.html',
  styleUrls: ['./discover.component.scss']
})
export class DiscoverComponent implements OnInit {
  discoverPosts: DiscoverPost[] = [];

  ngOnInit(): void {
    this.generateMockData();
  }

  private generateMockData() {
    const sampleImages = [
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e',
      'https://images.unsplash.com/photo-1522205408450-add114ad53fe',
      'https://images.unsplash.com/photo-1498050108023-c5249f4df085',
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb'
    ];

    this.discoverPosts = Array.from({ length: 10 }).map((_, i) => ({
      title: `Discover Post ${i + 1}`,
      description:
        'A fascinating post exploring AI, design, and creativity. Dive in to explore something new.',
      author: `User ${Math.floor(Math.random() * 50) + 1}`,
      likes: Math.floor(Math.random() * 1000),
      tags: ['AI', 'Design', 'Trending', i % 2 === 0 ? 'Featured' : 'New'],
      image: sampleImages[i % sampleImages.length]
    }));
  }

  likePost(index: number) {
    this.discoverPosts[index].likes++;
  }

  viewPost(index: number) {
    const post = this.discoverPosts[index];
    alert(`✨ Viewing: ${post.title}\n\n${post.description}`);
  }
}
