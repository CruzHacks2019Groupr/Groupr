var app = function() {
    Vue.config.devtools = true;
    var self = {};

    Vue.config.silent = false; // show all warnings
    
    self.changeEvent = function(num, bool) {
        if(self.vue.userData.bio != null) self.vue.edit_profile = false
        self.vue.curr_event = num
        if (self.vue.events[num].isIn)
            self.getNextMatch()
    }


    self.accept = function(){

        $("#suggestedUserView").fadeTo(400,0, function(){
            self.vue.loading = true
            var request = {
                "eventID": self.vue.events[self.vue.curr_event].id,
                "acceptedUser": self.vue.suggested_usr.id
            }
            var url = "/accept/" + "?" + $.param(request);

            $.getJSON(url, function (data) {
                console.log(data)
                if(typeof data.group != "undefined") {
                    self.vue.events[self.vue.curr_event].group = data.group
                }
                self.getNextMatch()
                 $("#suggestedUserView").fadeTo(600,1)
            })
        })

    };

    self.decline = function(){
        $("#suggestedUserView").fadeTo(400,0, function(){
            self.vue.loading = true
            var request = {
                "eventID": self.vue.events[self.vue.curr_event].id
            }
            var url = "/decline/" + "?" + $.param(request);

            $.getJSON(url, function (data) {
                console.log(data)
                self.getNextMatch()
                $("#suggestedUserView").fadeTo(600,1)
            })
        })

    };

    self.getNextMatch = function(){
        self.vue.confirmReject = false
        var request = {
            "eventID": self.vue.events[self.vue.curr_event].id
        }
        var url = "/getNextMatch/" + "?" + $.param(request);

        $.getJSON(url, function (data) {
            self.vue.loading = false
            console.log(data)
            self.vue.suggested_usr = data.suggested_usr
        })
    };

    self.loadData = function(){
        var request = {
        }
        var url = "/loadData/" + "?" + $.param(request);
        
        $.getJSON(url, function (data) {
            
            console.log(data)
            self.vue.events = data.events
            self.vue.userData = data.userData
            if(data.events.length != 0)
                self.vue.curr_event = 0
            if(data.events.length != 0 && self.vue.events[0].isIn)
                self.getNextMatch()
            if (self.vue.userData.bio == null){
                self.vue.edit_profile = true
            }
            self.vue.page_loaded = true;
            $("#vue-div").delay(100).fadeIn();

 
        })
    };

    self.forceGroups =function(){
        var request = {
            "eventID": self.vue.events[self.vue.curr_event].id
        }
        var url = "/forceGroups/" + "?" + $.param(request);

        $.getJSON(url, function (data) {
            console.log(data)
        })
    }

    self.testFunc1 =function(){
        $("#mainPage").fadeTo(300,0)
        self.vue.loading = true
        var request = {
        }
        var url = "/testFunc1/" + "?" + $.param(request);

        $.getJSON(url, function (data) {
            console.log(data)
            self.vue.loadData()
            $("#mainPage").fadeTo(300,1)
            self.vue.loading = false
        })
    }
    self.rejectGroup =function(){
        if(self.vue.confirmReject == false){
            self.vue.confirmReject = true
        }
        else{
            $("#mainPage").fadeTo(300,0)
            loading = true
            var request = {
                "eventID": self.vue.events[self.vue.curr_event].id
            }
            var url = "/rejectGroup/" + "?" + $.param(request);

            $.getJSON(url, function (data) {
                console.log(data)
                self.loadData()
                $("#mainPage").fadeTo(300,1)
            })
        }

    }

    self.testFunc2 =function(){
        var request = {
        }
        var url = "/testFunc2/" + "?" + $.param(request);

        $.getJSON(url, function (data) {
            console.log(data)
        })
    }

    // Complete as needed.
    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        computed: {
            inputFileName : function() {
                if(this.fileName == null){
                    return 'Profile Photo <small>(optional)</small>'
                }
                else{
                    fname = this.fileName.split("\\");
                    return fname[fname.length- 1];
                }
            },
        },
        data: {
            //booleans
            page_loaded: false,
            edit_profile: false,
            suggested_usr: {
                name: "",
                id: -1,
            },
            logged_in: true,
            curr_event: -1,
            events: [],
            userData: {
                image: null,
            },
            fileName: null,
            loading: false,
            confirmReject: false,

        },
        methods: {

            accept: self.accept,
            decline: self.decline,
            getNextMatch: self.getNextMatch,
            loadData: self.loadData,
            changeEvent: self.changeEvent,
            testFunc1: self.testFunc1,
            testFunc2: self.testFunc2,
            forceGroups: self.forceGroups,
            rejectGroup: self.rejectGroup,
            toggleEditMode: function(){
                if(this.userData.bio != null) this.edit_profile = !this.edit_profile
            }
        }

    });

    //self.load();
    self.loadData()
    //self.getNextMatch()
    

    

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});

    $(document).ready(function(){
        $('[data-toggle="tooltip"]').tooltip(); 
    });  