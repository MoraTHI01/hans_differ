/**
 * Binary tree node containing interval information and an
 * optional index for leaf nodes
 */
class IntervalNode {
  start: number;
  end: number;
  index?: number;
  left?: IntervalNode;
  right?: IntervalNode;

  /**
   * Creates a new `IntervalNode` from an interval and optionally left and right child nodes
   *
   * @param {number} start - Start of the interval
   * @param {number} end - End of the interval (either exlusive or inclusive depending on the overlap mode in the {@link IntervalTree})
   * @param {IntervalNode?} left - The left child node
   * @param {IntervalNode?} right - The right child node
   */
  constructor(start: number, end: number, left?: IntervalNode, right?: IntervalNode) {
    this.start = start;
    this.end = end;
    this.left = left;
    this.right = right;
  }

  /**
   * Convenience function for getting the node interval as a two element list
   *
   * @returns {[number, number]} The start and end of the node interval in a list
   */
  interval(): [number, number] {
    return [this.start, this.end];
  }
}

/**
 * A simple binary search tree implementation for finding an interval from a single point.
 * It assumes all intervals to be sorted and continuous for simplicity, only optionally overlapping such that the end and start of two following intervals are the same.
 */
export class IntervalTree {
  length: number;
  #realIndices: number[];
  #leftChecker: (point: number, end: number) => boolean;
  #root?: IntervalNode;

  /**
   * Constructs an `IntervalTree` from a list of sorted, continuous intervals.
   *
   * @param {[number, number][]} segments - A list of sorted, continuous intervals
   * @param {boolean} endOverlap - If true, the ends and starts of following intervals may overlap.
   *                               Otherwise, only exclusive intervals are allowed.
   */
  constructor(segments: [number, number][], endOverlap: boolean = true) {
    // TODO: Filters out null segments as a workaround for missing intervals from the transcript
    [segments, this.#realIndices] = segments.reduce(
      ([newSegments, indices]: [[number, number][], number[]], segment, index) => {
        if (segment !== null) {
          newSegments.push(segment);
          indices.push(index);
        }
        return [newSegments, indices];
      },
      [[], []],
    );

    this.length = segments.length;
    this.#leftChecker = endOverlap
      ? (point: number, end: number) => point < end
      : (point: number, end: number) => point <= end;

    const length = segments.length;
    if (length === 0) {
      return;
    }

    // Assumes segments are sorted and non-overlapping for efficiency
    const lastIndex = length - 1;
    this.#root = new IntervalNode(segments[0][0], segments[lastIndex][1]);
    const queue: [IntervalNode, number, number][] = [[this.#root, 0, lastIndex]];

    // Constructs the interval tree top-down in breadth-first order from the sorted segments
    let state;
    while ((state = queue.shift())) {
      const [node, start, end] = state;
      if (start === end) {
        node.index = start;
        continue;
      }

      const middle = start + Math.floor((end - start) / 2);

      node.left = new IntervalNode(node.start, segments[middle][1]);
      queue.push([node.left, start, middle]);

      const rightStart = middle + 1;
      node.right = new IntervalNode(segments[rightStart][0], node.end);
      queue.push([node.right, rightStart, end]);
    }
  }

  /**
   * Finds the interval node containing the given `point` unless the `point` is out of
   * range of the root interval
   *
   * @param {number} point - The point to look up in the tree
   *
   * @return {IntervalNode?} The leaf node whose interval contains the `point`
   * or `undefined` if the `point` is out of range of the root interval
   */
  #findNode(point: number): IntervalNode | undefined {
    let current = this.#root;
    // The only way the point can't be found with contiguous intervals is if
    // the tree is empty or the point is outside the root interval
    if (!current || point < current.start || point > current.end) {
      return;
    }

    while (current.left) {
      // current.right is known to be non-null since every node has either none or both children
      current = this.#leftChecker(point, current.left.end) ? current.left : (current.right as IntervalNode);
    }

    return current;
  }

  /**
   * Finds the interval containing the given `point` unless the `point` is out of
   * range of the root interval
   *
   * @param {number} point - The point to look up in the tree
   *
   * @return {[number, number]} The interval as a list of the form `[start,
   * end]` which may be either inclusive or exclusive depending on the value of
   * `endOverlap` or `undefined` if the `point` is out of range of the root interval
   * @see {@link IntervalTree}
   */
  findInterval(point: number): [number, number] | undefined {
    return this.#findNode(point)?.interval();
  }

  /**
   * Finds the index of the segment whose interval contains the given `point`
   * unless the `point` is out of range of the root interval
   *
   * @param {number} point - The point to look up in the tree
   *
   * @return {number} The index of the interval containing the given `point` or
   * `undefined` if the `point` is out of range of the root interval
   */
  findIndex(point: number): number | undefined {
    // TODO: Maps to an index in the unfiltered segment list as a workaround for missing intervals
    const index = this.#findNode(point)?.index;
    if (index === undefined) {
      return index;
    }
    return this.#realIndices[index];
  }
}
