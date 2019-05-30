# raspberrylogger
A Race Tech protocol datalogger intended to run on a raspberry pi

Its very much a work in-progress.  The intention was for this to sit inline between an Adaptronic ECU and a RaceTech dash.  Due to the complexity of the variable length messages and checksums it was necessary to decode and insert timestamps into the messages, somthing we struggled to do in realtime.  This project is a historical archive of the work.

### Sample Data
Race Tech provide data samples on their website, with many examples located here ...

https://www.race-technology.com/gb/racing/downloads-documentation/software-downloads/sample-data-sets

### Authors
Jeremy Blythe wrote the original decoder, with command line utils by Chris Fane.

### Disclaimer
This project is in no way associated with Race Technology, and simply makes use of publically distributed protocol specifications.
