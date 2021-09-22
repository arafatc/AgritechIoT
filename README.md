# AgritechIoT
Cloud based software solution integrated with soil sensors and water sprinklers. It offers advanced adaptive irrigation software that saves water and energy costs, delivers crop yield increase while conserving the environment.


![image](https://user-images.githubusercontent.com/45310865/134349875-765062d9-e201-483c-9f65-b003fcef0e9f.png)


Introduction

Developed an innovative solution for farm water management.
Maintaining the right balance between water consumption and soil moisture management is crucial to get a good crop yield at efficient costs. Developed an automatic sprinkler system based on soil and air parameters, with information coming from embedded sensors.

Basic Requirements

This is a simple system to manage and actuate sprinklers based on soil temperature and moisture in a large farm. The same setup and technology can be replicated across various farms as needed, so scale is one of the key factors. It is deployed on AWS Cloud Computing infrastructure, for better data gathering, efficiency, and scale.

Real and simulated soil temperature & moisture sensors need to continuously feed data to the AWS Cloud, via AWS IoT Core. That data then can be streamed and acted upon accordingly. 

The system also fetches air temperature and humidity readings of the farm location, from an open weather API.

The initial soil sensor information is stored in a cloud database along with unique device ids and their lat/long coordinates. Similarly, information is stored about the sprinkler locations.

The farm has a predetermined topology when it comes to sensor and sprinkler locations. Each soil sensor comes under the range of a particular sprinkler. This is directly mapped in the system.

The system continuously monitors the incoming soil and air readings. Based on a reasonable linear difference algorithm it decides whether a particular soil sensor location requires water. If enough soil sensors (based on a predefined percentage) mapped to a sprinkler raise an alarm, the system sends a command to the sprinkler to turn on. Similarly, it decides when to turn them off.

The main features of the system are:

* Soil sensor and sprinkler simulators
* There are 5 soil sensors and 1 sprinklers, simulated in IoT core with each sensor mapped to a particular sprinkler. This can can be easily scaled to multiple devices.
* The IoT Core Things is publishing and receiving information (*You are free to add 1, or more, real devices with temperature and moisture sensors if you have them available)
* Air temperature and humidity information of a representative lat/long based location of the farm are retrieved from  https://openweathermap.org/api 
* This can be directly sent to your computing solution, via an EC2 instance, local machine, or a Lambda function
* AWS IoT Core receives all the data, messaging back to the sprinklers, and passing the data further down to streaming and database entities
* DynamoDB is used to store raw information and decisions and used DynamoDB streams to pass data to Microservice ( implemented as Lambda functions)

Advanced Features

* Water consumption trends based on air temperature and humidity

(*Below are Not yet completed on 22/09/2021)
* The sensors and actuators could be auto-provisioned using a program that can use AWS IoT Core APIs. It should be possible to set up a soil sensor or sprinkler through the command line (or through a UI) to register a thing with a unique name, with appropriate mapping. It should deliver the necessary keys and certificates for the device to connect and transfer data. 
* Real-time visual dashboard of the activity. This can show an entity-based or a map-based view of the current sensor states and sprinkler activity
* Areas of low and high water consumption
* Visual representations of farm water usage patterns, with location information (pie-charts, bar-charts, bee-hives)
