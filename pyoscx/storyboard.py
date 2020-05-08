import xml.etree.ElementTree as ET

from .actions import _Action

from .triggers import EmptyTrigger
from .utils import EntityRef
from .scenario import ParameterDeclarations


class StoryBoard():
    """ The StoryBoard class creates the storyboard of OpenScenario
        
        Parameters
        ----------
            init (Init): the init part of the storyboard

            stoptrigger (Valuetrigger, Entitytrigger or EmptyTrigger): 
                the stoptrigger of the storyboard (optional)
                Default (EmptyTrigger) 

        Attributes
        ----------

            init (Init): the init of the storyboard

            stoptrigger (Valuetrigger, Entitytrigger or EmptyTrigger): 
                the stoptrigger

            stories (list of Story): all stories of the scenario

        Methods
        -------
            add_story (story)
                adds a story to the storyboard

            get_element()
                Returns the full ElementTree of the class


    """
    def __init__(self,init,stoptrigger=EmptyTrigger('stop')):
        """ initalizes the storyboard

        Parameters
        ----------
            init (Init): the init part of the storyboard

            stoptrigger (Valuetrigger, Entitytrigger or EmptyTrigger): 
                the stoptrigger of the storyboard (optional)
                Default (EmptyTrigger) 

        """
        self.init = init
        self.stoptrigger = stoptrigger
        self.stories = []

    def add_story(self,story):
        """ adds a story to the storyboard

        Parameters
        ----------
            story (Story): the story to be added 

        """
        self.stories.append(story)

    def get_element(self):
        """ returns the elementTree of the Storyboard

        """
        element = ET.Element('Storyboard')
        element.append(self.init.get_element())
        if not self.stories:
            raise ValueError('no stories available for storyboard')
        
        for story in self.stories:
            element.append(story.get_element())
        element.append(self.stoptrigger.get_element())

        return element

class Init():
    """ the Init class, creates the init part of the storyboard
        
        Attributes
        ----------
            initactions (dir: {entityname: Action}): a directory 
                containing all init actions of the scenario
                
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_init_action(entityname, action):
                adds an action to the init

    """
    def __init__(self):
        """ initalize the Init class

        """
        self.initactions = {}

    def add_init_action(self,entityname,action):
        """ add_init_action adds an Action to the init.

        Parameters
        ----------
            entityname (str): name of the entity to add the action to
            Action (*Action): Any action to be added (like TeleportAction)
            
        """
        if entityname not in self.initactions:
            self.initactions[entityname] = []

        self.initactions[entityname].append(action)

    def get_element(self):
        """ returns the elementTree of the Init

        """
        element = ET.Element('Init')
        actions = ET.SubElement(element,'Actions')
        
        for i in self.initactions:
            private = ET.SubElement(actions,'Private',attrib={'entityRef':i})
            for j in self.initactions[i]:
                private.append(j.get_element())


        return element

class Story():
    """ The Story class creates a story of the OpenScenario
        
        Parameters
        ---------- 
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the Story
            
        Attributes
        ----------
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the story (optional)

            acts (list of Act): all acts belonging to the story

        Methods
        -------
            add_act(act)
                adds an act to the story

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, name, parameters=ParameterDeclarations()):
        """ initalizes the Story class

        Parameters
        ---------- 
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the Story
        """
        self.name = name

        self.acts = []

        self.parameter = parameters

    def add_act(self,act):
        """ adds an act to the story

        Parameters
        ---------- 
            act (Act): act to add to the story

        """
        self.acts.append(act)

    def get_attributes(self):
        """ returns the attributes as a dict of the Story

        """
        return {'name':self.name}
    
    def get_element(self):
        """ returns the elementTree of the Story

        """
        element = ET.Element('Story',attrib=self.get_attributes())
        element.append(self.parameter.get_element())
        if not self.acts:
            raise ValueError('no acts added to the story')
        for a in self.acts:
            element.append(a.get_element())
        return element

class Act():
    """ the Act class creates the Act of the OpenScenario
        
        Parameters
        ----------
            name (str): name of the act

            starttrigger (*Trigger): starttrigger of the act

            stoptrigger (*Trigger): stoptrigger of the act (optional)
            
        Attributes
        ----------
            name (str): name of the act

            starttrigger (*Trigger): starttrigger of the act

            stoptrigger (*Trigger): stoptrigger of the act (optional)

            maneuvergroup (list of ManeuverGroup): list of ManeuverGroups belonging to the act

        Methods
        -------
            add_maneuver_group(maneuvergroup)
                adds a maneuvuergroup to the act

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,starttrigger,stoptrigger=None):
        """ Initalize the Act

        Parameters
        ----------
            name (str): name of the act

            starttrigger (*Trigger): starttrigger of the act

            stoptrigger (*Trigger): stoptrigger of the act (optional)
                Default: Emptytrigger

        """
        self.name = name
        self.starttrigger = starttrigger
        if stoptrigger == None:
            self.stoptrigger = EmptyTrigger('stop')
        else:
            self.stoptrigger = stoptrigger
        self.maneuvergroup = []

    def add_maneuver_group(self,maneuvergroup):
        """ adds a maneuvuergroup to the act

        Parameters
        ----------
            name (str): name of the act

        """
        self.maneuvergroup.append(maneuvergroup)

    def get_attributes(self):
        """ returns the attributes as a dict of the Act

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Act

        """
        element = ET.Element('Act',attrib=self.get_attributes())
        if not self.maneuvergroup:
            raise ValueError('no maneuver group added to the act')
        for mangr in self.maneuvergroup:
            element.append(mangr.get_element())

        element.append(self.starttrigger.get_element())
        element.append(self.stoptrigger.get_element())
        return element

class ManeuverGroup():
    """ the ManeuverGroup creates the ManeuverGroup of the OpenScenario
        
        Parameters
        ----------
            name (str): name of the ManeuverGroup

            maxexecution (int): maximum number of iterations

            selecttriggeringentities (bool): Have no idea what this does ??? TODO: check

        Attributes
        ----------
            name (str): name of the ManeuverGroup

            maxexecution (int): maximum number of iterations

            selecttriggeringentities (bool): Have no idea what this does ??? TODO: check

            maneuvers (list of Maneuver): the maneuvers in the ManeuverGroup

            actprs (_Actors): all actors of the ManeuverGroup

        Methods
        -------
            add_maneuver(Maneuver)
                adds a maneuver to the ManeuverGroup

            add_actor(entity)
                adds an actor to the ManeuverGroup

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,maxexecution=1,selecttriggeringentities = False):
        """ initalize the ManeuverGroup

            Parameters
            ----------
                name (str): name of the ManeuverGroup

                maxexecution (int): maximum number of iterations

                selecttriggeringentities (bool): Have no idea what this does ??? TODO: check
        
        """
        self.name = name
        self.maxexecution = maxexecution
        self.actors = _Actors(selecttriggeringentities)
        self.maneuvers = []
        # TODO:fix catalogue

    
    def add_maneuver(self,maneuver):
        """ adds a maneuver to the ManeuverGroup
            
        Parameters
        ----------
            maneuver (Maneuver): maneuver to add

        """
        self.maneuvers.append(maneuver)

    def add_actor(self,entity):
        """ adds an actor to the ManeuverGroup
            
        Parameters
        ----------
            entity (str): name of the entity to add as an actor

        """
        self.actors.add_actor(entity)

    def get_attributes(self):
        """ returns the attributes as a dict of the ManeuverGroup

        """
        return {'name':self.name,'maximumExecutionCount':str(self.maxexecution)}

    def get_element(self):
        """ returns the elementTree of the ManeuverGroup

        """
        element = ET.Element('ManeuverGroup',attrib=self.get_attributes())
        element.append(self.actors.get_element())
        for man in self.maneuvers:
            element.append(man.get_element())
        return element



class _Actors():
    """ _Actors is used to create the actors of a ManeuverGroup
        
        Parameters
        ----------
            selectTriggeringEntities (bool): ???
                Default: False

        Attributes
        ----------
            selectTriggeringEntities (bool): ???

            actors (list or EntityRef): all actors to add to the element

        Methods
        -------
            add_actor(actor)
                adds an actor 

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, selectTriggeringEntities=False):
        """ initalize the _Actors

            Parameters
            ----------
                selectTriggeringEntities (bool): ???
                    Default: False

        """
        self.actors = []
        self.select = selectTriggeringEntities

    

    def add_actor(self,entity):
        """ adds an actor to the list of actors
            
            Parameters
            ----------
                entity (str): name of the entity

        """
        self.actors.append(EntityRef(entity))

    def get_attributes(self):
        """ returns the attributes of the _Actors as a dict

        """
        return {'selectTriggeringEntities':str(self.select)}

    def get_element(self):
        """ returns the elementTree of the _Actors

        """
        if not self.actors:
            raise ValueError('no actors are set')

        element = ET.Element('Actors',attrib=self.get_attributes())
        for ent in self.actors:
            element.append(ent.get_element())
        return element



class Maneuver():
    """ The Maneuver class creates the Maneuver of OpenScenario
        
        Parameters
        ----------
            name (str): name of the Maneuver

        Attributes
        ----------
            name (str): name of the Maneuver

            events (list of Event): all events belonging to the Maneuver

        Methods
        -------
            add_event (event)
                adds an event to the Maneuver
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name):
        """ initalizes the Maneuver
        Parameters
        ----------
            name (str): name of the Maneuver

        """
        self.name = name
        self.events = []
        # TODO:add parameter declaration

    def add_event(self,event):
        """ adds an event to the Maneuver

        Parameters
        ----------
            name (Event): the event to add to the Maneuver

        """
        self.events.append(event)

    def get_attributes(self):
        """ returns the attributes as a dict of the Maneuver

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Maneuver

        """
        if not self.events:
            raise ValueError('no events added to the maneuver')

        element = ET.Element('Maneuver')
        for event in self.events:
            element.append(event.get_element())

        return element

class Event():
    """ the Event class creates the event of OpenScenario
        
        Parameters
        ----------
            name (str): name of the event

            priority (str): what priority the event has TODO: add definition

            maxexecution (int): the maximum allowed executions of the event
                Default: 1

        Attributes
        ----------
            name (str): name of the event

            priority (str): what priority the event has TODO: add definition

            maxexecution (int): the maximum allowed executions of the event
                
            action (list of actions): all actions belonging to the event

            trigger (*Trigger): a start trigger to the event

        Methods
        -------
            add_trigger()
                adds an trigger to the event

            add_action()
                adds an action to the event (can be called multiple times)

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,priority,maxexecution=1):
        self.name = name
        self.priority = priority
        self.action = []
        self.trigger = None
        self.maxexecution = maxexecution

    def add_trigger(self,trigger):
        """ adds a starging trigger to the event

        Parameters
        ----------
            trigger (*Trigger): Adds a trigger to start the event (not EmptyTrigger)

        """
        self.trigger = trigger

    def add_action(self,actionname,action):
        """ adds an action to the Event, multiple actions can be added and will be ordered as added.

        Parameters
        ----------
            action (*Action): any action to be added to the event

        """
        self.action.append(_Action(actionname,action))

    def get_attributes(self):
        """ returns the attributes as a dict of the Event

        """
        return {'name':self.name,'priority':self.priority,'maximumExecutionCount':str(self.maxexecution)}

    def get_element(self):
        """ returns the elementTree of the Event

        """
        if not self.action:
            raise ValueError('no action(s) set')
        if not self.trigger:
            raise ValueError('no trigger set')

        element = ET.Element('Event',attrib=self.get_attributes())
        for action in self.action:
            element.append(action.get_element())

        element.append(self.trigger.get_element())
        return element
