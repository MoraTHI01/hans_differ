Video Synchronization
=====================


Overview
--------

The video player currently consists of four or five main components:

- the video itself
- the transcript
- the transcript search
- markers for topics, questions and other information
- optional slides

To allow the user to more easily follow along with the lecture, most components are automatically synchronized with each-other when interacting with them using the `SetPosition` event interface. The figure gives a high level overview of how events are handled and emitted by each component. Note that the high level event handling approach is independent of the specifics of how each component internally uses events when they are received or when exactly events are fired on interaction.

The SetPositionEvent Interface
------------------------------

The `SetPosition` event is defined by three fields, of which two are optional:

- The `position` field contains the timestamp in seconds as a floating point value to which all components should synchronize. The transcript, search, markers and slides use intervals internally. In these cases, the `position` is the start time of the interval. E.g. when a user changes slides, time should be synchronized to where the lecturer starts talking about it.
- The `origin` field contains a unique string identifier of the component that fired the event. Even though it is technically optional, the field is used by most components to guard against receiving the events fired by themselves and potentially cause infinite loops. It also allows for handling synchronization events differently depending on their source.
- The `index` field optionally contains the target word index. This field is a simple optimization for the search and transcript components where this information is available. Without this field, a traversal of a binary search tree would be required to find the word index from the `position` timestamp.

The event is fired by all components and received by all of them except for the media search.

Interval Trees
--------------

Simple binary interval trees are constructed for the intervals in the transcript, marker and slide components. These allow finding a word, marker or slide index from the position timestamp in `O(log n)` instead of `O(n)` time.

Slide Synchronization
---------------------

In contrast to other components, slides are completely optional, and no synchronization will occur if they are missing. To optionally allow students to follow the slides independently of the video for context, it should also be possible to temporarily disable slide synchronization with the other components. When slide synchronization is disabled, the slide component will no longer receive or fire events. Instead, the transcript and markers are only synchronized with the video.
