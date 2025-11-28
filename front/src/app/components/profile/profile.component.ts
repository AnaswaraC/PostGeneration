import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss'],
})
export class ProfileComponent {
  @Output() close = new EventEmitter<void>();
  @Output() logout = new EventEmitter<void>(); // ✅ new output for logout

  user = {
    name: 'Michelle M',
    role: 'Creative Explorer',
    bio: 'Exploring trends and creating stories with Pollyn ✨',
    avatar: '../../../assets/profile.jpg',
    stats: [
      { label: 'Posts', value: 42 },
      { label: 'Followers', value: '1.2k' },
      { label: 'Following', value: 180 },
    ],
  };

  onClose() {
    this.close.emit();
  }

  onLogout() {
    this.logout.emit(); // ✅ emit logout event
  }
}
