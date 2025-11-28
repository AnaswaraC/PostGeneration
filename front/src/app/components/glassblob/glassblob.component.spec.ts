import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GlassBlobComponent } from './glassblob.component';

describe('GlassblobComponent', () => {
  let component: GlassBlobComponent;
  let fixture: ComponentFixture<GlassBlobComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GlassBlobComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GlassBlobComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
