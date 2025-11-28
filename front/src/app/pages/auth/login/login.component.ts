import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  @Output() close = new EventEmitter<void>();
  email = '';
  password = '';

  onLogin() {
    console.log('Login attempted:', this.email, this.password);
  }

  closeLogin(event?: Event) {
    event?.stopPropagation();
    this.close.emit();
  }
}
