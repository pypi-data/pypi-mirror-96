fastABF is a fast and robust computation module for activity based funding (ABF). It helps to 
streamline the computation of ABF activities as per the National Efficient Price (NEP) 20-21 framework guidelines.  It covers the following major ABF activity types

- admitted acute
- admitted sub/non-acute
- non-admitted
- emergency department or emergency service

**Documentation**: [fastABF doc](https://greenlakemedical.github.io/fastABF/)

---
## Features

- **Fast to setup** - go from start to computing an example ABF episode within 5 minutes. Save *close to a month* of development and testing time!
- **Robust** - with python type hints, strong version control (via Poetry) and strong test coverage the code base is ready for use in backend systems.
- **Easy to understand and extend** - numerous comments and well structured organisation, ensure that health IT developers can easily use and extend these modules. 
- **Pain free** - The code aims to distill the numerous computations detailed in the IHPA NEP 20-21 computation documentation and guidelines. These span over **60 pages**. This is in addition to the HAC computation guidelines which span **over 40 pages**. The effort we have put into this is time that you can spend on making other innovative contributions (or taking several long walks :) ).
- **Lower bug count** - By leveraging a well tested and open source code base - developers can reduce the chance of introducing bugs into their ABF calculations by over 25-30%* 
- **Incorporates METeOR conventions** - The METeOR identifiers have been mapped to user friendly Python `Enum` names. Now instead of remembering the METeOR numerical identifiers you can use these human readable class names  - reducing the possibility of bugs and errors creeping in. 
- **HAC adjustment computations** - The detailed steps of the HAC adjustments are included as well. 
- **Remoteness calculations** - This code also contains the steps to obtain the remoteness values (from postcode and SA2 address). Hence it enables automatic extraction of the RA16 remoteness class)

<small>* based on the experience of the internal dev-team and bugs caught and resolved via type checking and testing during development.

**Glossary**
- [HAC]: hosptial acquired complications
- [IHPA]: Independent hospital pricing authority
- [METeOR]:  Metadata online registry 
- [ABF]: Activity based funding
- [NEP]: National efficient price

It is assumed that you are familiar with 
- python 
- the terminology and concepts of ABF.
