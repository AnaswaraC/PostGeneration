import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { IntroComponent } from './components/intro/intro.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { LoginComponent } from './pages/auth/login/login.component';
import { SignupComponent } from './pages/auth/signup/signup.component';
import { SequenceComponent } from './components/sequence/sequence.component';
import { GlassBlobComponent } from './components/glassblob/glassblob.component';
import { CreateComponent } from './components/create/create.component';
import { FormsModule } from '@angular/forms';
import { HistoryComponent } from './components/history/history.component';
import { DiscoverComponent } from './components/discover/discover.component';
import { FooterComponent } from './components/footer/footer.component';
import { ProfileComponent } from './components/profile/profile.component';

@NgModule({
  declarations: [
    AppComponent,
    IntroComponent,
    DashboardComponent,
    LoginComponent,
    SignupComponent,
    SequenceComponent,
    GlassBlobComponent,
    CreateComponent,
    HistoryComponent,
    DiscoverComponent,
    FooterComponent,
    ProfileComponent,

  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
        FormsModule,  
    RouterModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
