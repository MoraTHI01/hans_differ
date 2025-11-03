class PlayEvent {
  origin?: string;
  constructor(origin?: string) {
    this.origin = origin;
  }
}

class PauseEvent {
  origin?: string;
  constructor(origin?: string) {
    this.origin = origin;
  }
}

class SetPositionEvent {
  position: number;
  origin?: string;
  index?: number;

  constructor(position: number, origin?: string, index?: number) {
    this.position = position;
    this.origin = origin;
    this.index = index;
  }
}

class SetPageEvent {
  page: number;
  origin?: string;
  index?: number;

  constructor(page: number, origin?: string, index?: number) {
    this.page = page;
    this.origin = origin;
    this.index = index;
  }
}

export {PlayEvent, PauseEvent, SetPositionEvent, SetPageEvent};
