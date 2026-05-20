#import "@preview/charged-ieee:0.1.4": ieee

#show: ieee.with(
  title: [Improving Autonomous Robot Localization using GPS and IMU Data Fusion],
  abstract: [
    #lorem(20)
  ],
  authors: (
    (
      name: "Steffen Ullmann",
      organization: [Florida Polytechnic University],
      location: [Lakeland, FL, USA],
      email: "sullmann3121@floridapoly.edu"
    ),
  ),
  index-terms: (),
  bibliography: bibliography("./refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction
// Problem of uncertainty of GPS e.g. indoors --> Fusion is better
@netwok2020 @netwok2022.

//== Paper overview


= Methods <sec:methods>
#lorem(10)

$ a + b = gamma $ <eq:gamma>

#figure(
  placement: none,
  circle(radius: 15pt),
  caption: [A circle representing the Sun.]
) <fig:sun>

In @fig:sun you can see a common representation of the Sun, which is a star that is located at the center of the solar system.


In you see the planets of the solar system and their average distance from the Sun.
The distances were calculated with @eq:gamma that we presented in @sec:methods.