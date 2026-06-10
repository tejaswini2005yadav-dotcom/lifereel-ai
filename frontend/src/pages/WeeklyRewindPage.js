/**
 * LifeReel AI - WeeklyRewindPage View
 */
import { db } from '../utils/db.js';
import { RewindCard } from '../components/RewindCard.js';

export class WeeklyRewindPage {
  constructor() {
    this.carousel = null;
  }

  render() {
    const container = document.createElement('div');
    container.className = 'page-view rewind-container';

    const memories = db.getAll();
    
    container.innerHTML = `
      <div class="section-title-wrap" style="text-align: left; margin-bottom: 2rem;">
        <h2 class="section-title">Weekly Rewind</h2>
        <p class="section-subtitle">A cozy, slide-based recap of your recorded memories this week.</p>
      </div>

      <!-- Mount RewindCard Carousel -->
      <div id="carousel-mount"></div>

      <!-- Dashboard Footer stats summary blocks -->
      <div class="rewind-footer-summary" id="stats-summary-footer">
        <!-- Stats populated dynamically below -->
      </div>
    `;

    // Initialize slide deck
    this.carousel = new RewindCard(memories);
    container.querySelector('#carousel-mount').appendChild(this.carousel.render());

    // Populate bottom summary blocks
    const footer = container.querySelector('#stats-summary-footer');
    const totals = this.carousel.totals;

    const lastNodeText = memories.length > 0
      ? `Entry: "${memories[0].title}" was saved as your latest memory.`
      : 'No memories saved yet.';

    const stabilityText = memories.length <= 1
      ? 'Start adding memories to unlock mood analytics.'
      : `Balanced around "${totals.dominantMood}". You are doing great!`;

    footer.innerHTML = `
      <div class="recap-block-card">
        <div class="recap-icon-bubble"><i class="bi bi-clock-history"></i></div>
        <div class="recap-info-pane">
          <h4>Total Recording Time</h4>
          <p>${totals.totalDuration} seconds of voice recordings saved.</p>
        </div>
      </div>

      <div class="recap-block-card">
        <div class="recap-icon-bubble"><i class="bi bi-shield-check"></i></div>
        <div class="recap-info-pane">
          <h4>Calmness Index</h4>
          <p>${stabilityText}</p>
        </div>
      </div>

      <div class="recap-block-card">
        <div class="recap-icon-bubble"><i class="bi bi-check-all"></i></div>
        <div class="recap-info-pane">
          <h4>Latest Entry</h4>
          <p>${lastNodeText}</p>
        </div>
      </div>
    `;

    return container;
  }

  onMount() {}

  destroy() {
    if (this.carousel) {
      this.carousel.destroy();
    }
  }
}
