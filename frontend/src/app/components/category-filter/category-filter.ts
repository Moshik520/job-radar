import { Component, computed, ElementRef, inject, input, output, signal } from '@angular/core';
import { CATEGORY_GROUPS, CATEGORY_LABELS, Category, CategoryCount } from '../../models/job';

@Component({
  selector: 'app-category-filter',
  styleUrl: './category-filter.scss',
  templateUrl: './category-filter.html',
  host: {
    '(document:click)': 'onDocumentClick($event)',
    '(document:keydown.escape)': 'isOpen.set(false)',
  },
})
export class CategoryFilter {
  private readonly element = inject(ElementRef);

  readonly selected = input.required<Category[]>();
  readonly counts = input<CategoryCount[]>([]);
  readonly selectedChange = output<Category[]>();

  protected readonly isOpen = signal(false);
  protected readonly labels = CATEGORY_LABELS;

  // Only categories that have jobs right now, in the fixed group order.
  protected readonly groups = computed(() => {
    const countByCategory = new Map(this.counts().map((item) => [item.category, item.count]));
    return CATEGORY_GROUPS.map((group) => ({
      label: group.label,
      options: group.categories
        .filter((category) => countByCategory.has(category) || this.selected().includes(category))
        .map((category) => ({ category, count: countByCategory.get(category) ?? 0 })),
    })).filter((group) => group.options.length > 0);
  });

  protected readonly buttonLabel = computed(() => {
    const selected = this.selected();
    if (selected.length === 0) return 'All categories';
    if (selected.length === 1) return this.labels[selected[0]];
    return `${selected.length} categories`;
  });

  toggleOpen() {
    this.isOpen.update((open) => !open);
  }

  toggle(category: Category, checked: boolean) {
    const selected = this.selected();
    this.selectedChange.emit(
      checked ? [...selected, category] : selected.filter((item) => item !== category),
    );
  }

  clear() {
    this.selectedChange.emit([]);
  }

  onDocumentClick(event: MouseEvent) {
    if (!this.element.nativeElement.contains(event.target)) {
      this.isOpen.set(false);
    }
  }
}
