// =========================
// import required libraries
// =========================a

const Alexa = require("alexa-sdk")
const firebase = require("./firebase.js")

firebase.host = "alexaHomeSecurity.firebaseio.com"  // set the host for our Firebase database


// ============================
// create Alexa intent handlers
// ============================

const handlers = {
	"Unhandled": function() {
		// give a greeting message to user when they don't say a correct intent
		this.emit(":ask", "Welcome to sentinel. You may arm sentinel by saying 'arm', or you may disarm sentinel by saying 'disarm'. You may also check the status of sentinel by asking 'what is the status'. Finally, if you would like to rename a sensor, say 'rename sensor x to new name'. For example, 'rename sensor 0 to kitchen sensor'.")
	},
	"ArmIntent": function() {
		// set armed to true in database
		firebase.put("/armed", true).then(() => {
			// give status response to user
			this.emit(":tell", "Sentinel is now armed.")
		})
	},
	"DisarmIntent": function() {
		// set armed to false, delete all recorded events for this armed session (in database)
		Promise.all([firebase.put("/armed", false), firebase.delete("/events")]).then(() => {
			// give status response to user
			this.emit(":tell", "Sentinel is now disarmed.")
		})
	},
	"StatusIntent": function() {
		// get data from database
		firebase.get("/").then((data) => {
			// create speech response for user
			var speech = "Sentinel is "
			if(data.armed) {
				speech += "currently armed. "

				// get list of events
				var keys = Object.keys(data.events)
				if(keys.length == 0) {
					// there are no events listed
					speech += "No activity has been spotted by any of the sensors."
				} else {
					speech += "There " + (keys.length > 1 ? "have" : "has") + " been " + keys.length + " activity alerts today. Here are the latest alerts. "					
					
					// tell the user a maximum of 5 events
					var alerts = Math.min(keys.length, 5)

					// loop through all events and say where and when motion was detected
					for(var i = 0; i < alerts; i++) {
						var event = data.events[keys[i]]
						speech += data.sensors[event.sensor] + " detected motion at " + event.time + ".<break time='0.5s'/>"
					}
				}
			} else {
				// Sentinel is not armed right now
				speech += "not currently armed."
			}

			// give the built response to the user
			this.emit(":tell", speech)
		})
	},
	"RenameIntent": function() {
		// rename a sensor (sensor n) to (name)
		var sensor = this.event.request.intent.slots.Sensor.value
		var name = this.event.request.intent.slots.Name.value

		// update the name of the sensor in database
		firebase.put("/sensors/" + sensor, name).then(() => {
			// give status response to user
			this.emit(":tell", "Ok, sensor " + sensor + " is now named " + name + ".")
		})
	},
	"SessionEndedRequest": function() {
		// exit the function if the user tries at an unexpected time
		this.emit()
	}
}


// ========================
// main function for lambda
// ========================

exports.handler = function(event, context, callback) {  
	const alexa = Alexa.handler(event, context)
	alexa.registerHandlers(handlers)	// connect handler functions
	alexa.execute()						// execute function
}