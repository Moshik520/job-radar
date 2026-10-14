import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Category, CategoryCount } from '../../models/job';
import { CategoryFilter } from './category-filter';

describe('CategoryFilter', () => {
  let fixture: ComponentFixture<CategoryFilter>;
  let emitted: Category[][];
  const counts: CategoryCount[] = [
    { category: 'software', count: 281 },
    { category: 'qa', count: 40 },
    { category: 'sales', count: 86 },
  ];

  const page = () => fixture.nativeElement as HTMLElement;
  const find = (testId: string) => page().querySelector(`[data-testid="${testId}"]`) as HTMLElement | null;

  async function render(selected: Category[]) {
    fixture.componentRef.setInput('selected', selected);
    fixture.componentRef.setInput('counts', counts);
    await fixture.whenStable();
  }

  async function open() {
    find('category-filter-button')!.click();
    await fixture.whenStable();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [CategoryFilter] }).compileComponents();
    fixture = TestBed.createComponent(CategoryFilter);
    emitted = [];
    fixture.componentInstance.selectedChange.subscribe((value) => emitted.push(value));
  });

  it.each<[Category[], string]>([
    [[], 'All categories'],
    [['qa'], 'QA & Testing'],
    [['qa', 'sales'], '2 categories'],
  ])('the button says what is selected: %j → "%s"', async (selected, label) => {
    await render(selected);

    expect(find('category-filter-button')!.textContent).toContain(label);
  });

  it('is closed until the button is clicked', async () => {
    await render([]);
    expect(find('category-filter-panel')).toBeNull();

    await open();

    expect(find('category-filter-panel')).not.toBeNull();
  });

  it('lists only categories that have jobs, tech first, with their counts', async () => {
    await render([]);
    await open();

    const options = [...page().querySelectorAll('.option')].map(
      (option) => `${option.querySelector('.name')?.textContent?.trim()} ${option.querySelector('.count')?.textContent?.trim()}`,
    );
    expect(options).toEqual(['QA & Testing 40', 'Software Engineering 281', 'Sales & Business Development 86']);
  });

  it('adds a category when its box is checked', async () => {
    await render(['qa']);
    await open();

    const checkbox = find('category-option-sales')!.querySelector('input')!;
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change'));

    expect(emitted).toEqual([['qa', 'sales']]);
  });

  it('removes a category when its box is unchecked', async () => {
    await render(['qa', 'sales']);
    await open();

    const checkbox = find('category-option-qa')!.querySelector('input')!;
    expect(checkbox.checked).toBe(true);
    checkbox.checked = false;
    checkbox.dispatchEvent(new Event('change'));

    expect(emitted).toEqual([['sales']]);
  });

  it('clears the selection', async () => {
    await render(['qa', 'sales']);
    await open();

    find('category-filter-clear')!.click();

    expect(emitted).toEqual([[]]);
  });

  it('has no clear button when nothing is selected', async () => {
    await render([]);
    await open();

    expect(find('category-filter-clear')).toBeNull();
  });

  it('closes on a click outside it', async () => {
    await render([]);
    await open();

    document.body.click();
    await fixture.whenStable();

    expect(find('category-filter-panel')).toBeNull();
  });

  it('closes on Escape', async () => {
    await render([]);
    await open();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    await fixture.whenStable();

    expect(find('category-filter-panel')).toBeNull();
  });
});
