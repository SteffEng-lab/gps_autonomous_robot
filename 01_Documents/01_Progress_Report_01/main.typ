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
  bibliography: bibliography("../refs.bib"),
  figure-supplement: [Fig.],
)

= Introduction
- Problem of uncertainty of GPS e.g. indoors --> Fusion is better
- General about GPS --> disadvantages
- Why Fusion with IMU Data
- GOal of this project: see Readme.md



= Methods <sec:methods>
Progress:
- Can receive GPS messages from USB over ttyACM0 in Linux