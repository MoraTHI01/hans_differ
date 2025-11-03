import {expect, test} from "vitest";
import {IntervalTree} from "@/discreteIntervalTree";

test("search tree", () => {
  const testIntervals: [number, number][] = [
    [0, 4],
    [5, 8],
    [9, 10],
    [10, 45],
    [46, 49],
    [50, 57],
    [58, 62],
    [63, 69],
    [70, 75],
  ];

  const tree = new IntervalTree(testIntervals);

  expect(tree.length).toBe(9);
  expect(tree.findInterval(15)).toEqual([10, 45]);
  expect(tree.findIndex(7)).toBe(1);
  // Should match [10, 45] with overlap enabled
  expect(tree.findIndex(10)).toBe(3);
});
