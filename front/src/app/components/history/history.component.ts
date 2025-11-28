import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

interface PostHistory {
  title: string;
  description: string;
  caption?: string;
  date: string;
  tags?: string[];
}

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {
  history: PostHistory[] = [];
  filteredHistory: PostHistory[] = [];
  searchQuery = '';

  ngOnInit(): void {
    this.loadHistory();
    this.filteredHistory = [...this.history];
  }

  private loadHistory(): void {
    try {
      const stored = localStorage.getItem('postHistory');
      this.history = stored ? JSON.parse(stored) : this.getPlaceholderHistory();
    } catch {
      this.history = this.getPlaceholderHistory();
    }
  }

  applyFilter(): void {
    const q = this.searchQuery.toLowerCase().trim();
    this.filteredHistory = !q
      ? [...this.history]
      : this.history.filter(post =>
          [post.title, post.description, post.caption || '', ...(post.tags || [])]
            .join(' ')
            .toLowerCase()
            .includes(q)
        );
  }

  viewPost(index: number): void {
    const post = this.filteredHistory[index];
    alert(`📜 ${post.title}\n\n${post.description}\n\n${post.caption || ''}`);
  }

  deletePost(index: number): void {
    const post = this.filteredHistory[index];
    if (confirm(`Delete "${post.title}"?`)) {
      const originalIndex = this.history.indexOf(post);
      this.history.splice(originalIndex, 1);
      localStorage.setItem('postHistory', JSON.stringify(this.history));
      this.applyFilter();
    }
  }

  private getPlaceholderHistory(): PostHistory[] {
    const now = new Date().toISOString();
    return Array.from({ length: 10 }).map((_, i) => ({
      title: `Sample Post ${i + 1}`,
      description: `This is a sample description for post #${i + 1}.`,
      caption: i % 2 === 0 ? 'Example caption text.' : '',
      date: now,
      tags: ['Demo', 'History', `Tag${i % 5}`]
    }));
  }
}
