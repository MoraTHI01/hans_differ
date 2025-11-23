class LmsGatedAccessDetails {
  constructor(init?: Partial<LmsGatedAccessDetails>) {
    Object.assign(this, init);
  }
  type?: string;
  lms_name?: string;
  course_id?: string;
}

export {LmsGatedAccessDetails};
