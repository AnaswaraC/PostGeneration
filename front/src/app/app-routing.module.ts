import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IntroComponent } from './components/intro/intro.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { SequenceComponent } from './components/sequence/sequence.component';

const routes: Routes = [
  // Default route → redirect to intro
  { path: '', redirectTo: 'intro', pathMatch: 'full' },

  // Core app routes
  { path: 'intro', component: IntroComponent },
  { path: 'sequence', component: SequenceComponent },
  { path: 'dashboard', component: DashboardComponent },

  // Wildcard fallback
  { path: '**', redirectTo: 'intro' }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, {
      scrollPositionRestoration: 'enabled',
      anchorScrolling: 'enabled',
      scrollOffset: [0, 80],
    }),
  ],
  exports: [RouterModule],
})
export class AppRoutingModule {}
