import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.scss'],
})
export class SignupComponent {
  @Output() close = new EventEmitter<void>();
  name = '';
  email = '';
  password = '';

  onSignup() {
    console.log('Signup attempted:', this.name, this.email, this.password);
  }

  closeSignup(event?: Event) {
    event?.stopPropagation();
    this.close.emit();
  }
}
