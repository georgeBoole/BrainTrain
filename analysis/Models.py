import random
import sys
import DataProcessing

class Session(object):
    """
    Connects BrainControl data points to a unified session in case further analysis is necessary.

    Associates data points with individual users to establish user patterns.  Also makes trend-spotting
    possible, provides a more robust way to interface with individual user variations, and aggregates
    user-level data.

    Syntax: sessobj = Session(session_number, start_time, username, label_key, session_data)
    Note that session_data should be passed in as list of all of the data points
    
    """

    def __init__(self, sessnum, start_time, username, label_key, session_data):
        self.sessnum = sessnum
        self.start_time = start_time
        self.username = username
        self.data = session_data
        self.features = self.get_features()
        self.label_key = label_key
        self.make_data_points()

    def get_features(self):
        """
        Get the list of feature keys for a random data point in the session.

        Returns the feature keys of the randomly selected entry.
        
        """

        num_entries = len(self.data)
        # Choose a random data point
        entry_num = random.randint(1, num_entries) - 1
        target_entry = self.data[entry_num]
        return target_entry.keys()

    def list_features(self):
        "Returns a list of all of the feature KEYS in this session file"

        return self.features

    def get_value_by_feature(self, featurename):
        "Returns a list of all data points for a given feature"

        if self.feature_map is not None:
            return self.feature_map[featurename]

    def make_data_points(self):
        "Creates a list of all data points recorded in this session"

        self.datapoints = []
        for datapoint in self.data:
            point_user = self.username
            point_sessnum = self.sessnum
            point = DataPoint(point_user, point_sessnum,  datapoint)
            self.datapoints.append(point)

    def get_data_points(self):
        "Returns all of the session's data points"

        return self.datapoints

    def get_label_keys(self):
        "Returns all of the values for the label category"

        labels = map(lambda x: x.get_feature(self.label_key), self.datapoints)
        return labels


class Featureset(object):
    """
    Object to track the features in use.

    Syntax: Featureset(label_key, [featureset])
    Note: Including the featureset is optional on initialisation.
    Features can be added one at a time using this method:
    Featureset.add_feature('featurename')

    Instances of Featureset are meant to take the first data line
    from each session to verify features are aligned.
    Syntax: Featureset.check_features({data dictionary})
    Returns True if features are good, otherwise False

    """

    def __init__(self, label_key='label', feature_set=None):
        # If the user gives us a feature set, use it. Else, empty list.
        if feature_set is not None:
            self.features = feature_set
        else:
            self.features = []
        self.label_key = label_key

    def add_feature(self, feature_name):
        """
        Add a feature to the featureset list.

        Returns :True if successful.
        
        """

        if feature_name not in self.features:
            self.features.append(feature_name)
        return True

    def check_features(self, data):
        """
        Compare session featureset to existing featureset.
        Pass in the raw datapoint data to check for featureset matching.

        Returns :True if successful, :False if not.
        
        """

        # Get feature keys for the current session
        session_features = data
        # If there are no features in the feature set, record
        # the features from the current session
        if len(self.features) == 0:
            self.features = session_features
        # Otherwise, check for featureset match
        else:
            for k in session_features:
                if k not in self.features:
                    return False
        return True

    def get_label_key(self):
        "Return the name of the primary key for prediction."

        return self.label_key

    def set_label_values(self, label_vals):
        "Set the possible values for the primary key."

        self.label_values = label_vals

    def get_label_values(self):
        "Return a list of the possible values of the prediction key."

        return self.label_values

    def get_features(self):
        "Return a list of the feature keys."

        return self.features
    

class DataPoint(object):
    """
    Structured class for individual datapoint objects.
    This class will be the core of all operations, as it will allow
    for curation at a much finer grain than any of the other classes.

    Datapoints are the individual points of measurement taken in each session.

    Syntax: DataPoint(user, session_number, data)
    
    """

    def __init__(self, username, sessnum, data):
        """
        Instantiate a DataPoint object with user, session, and content
        awareness.

        :username is the username string taken from the session file key 'user'
        
        :sessnum is the user session number found in key 'session_number'

        :data is the set of data points taken in the session.  From
        the unpickled file, this is unpickled_contents['data'].
        The keys of the :data dictionary should be feature names,
        and the values should be observed values.
        
        """

        self.username = username
        self.sessnum = sessnum
        self.data = data

    def get_feature(self, feature_name):
        "Return the value of a single feature on this point."

        return self.data[feature_name]

    def get_features(self):
        "Return all of the features for this point."

        return self.data

    def get_full_data(self):
        "Return data with username and session number for processing."

        return { 'user': self.username, 'sessnum': self.sessnum, 'data': self.data }

    def get_user(self):
        "Return the username associated with the point."

        return self.username

    def get_sessnum(self):
        "Return the session number associated with the point."

        return self.sessnum


class TrainingSet(object):
    """
    Container class for operating on all of the training data.  This is where all the
    calls are going out from.

    Syntax: TrainingSet(label_key_name, full_training_set)
    Where label_key_name is the string keyname of the independent variable for which we are 
    classifying (e.g. 'label')
    and
    full_training_set is a list of the contents of all of the output files.

    """


    def __init__(self, keyname, training_data):
        """
        Initialize the TrainingSet class.

        This class contains Session objects, which represent single sessions of training
        data on a user-by-user basis.  Session objects are passed with their member DataPoints
        to the DataProcessing module where they can be analyzed and manipulated.

        :keyname represents the name of the indepdendent variable for which we will try to
        make predictions.
        :training_data represents the file contents of the saved session
        files, passed to the initializer as a list of file contents.

        """

        # Create a new featureset object and pass it the name of the prediction target variable
        self.featureset = Featureset(keyname)
        self.classify_on_key = keyname
        self.training_data = training_data
        # Kick off the training session by actually creating session objects in self.sessions
        if self.parse() is True:
            # Now create Data Processing objects and pass all of the sessions and features
            self.processor = DataProcessing.DataProcessor(self.featureset, self.sessions)
            # Do more things with the DataProcessor...
        else:
            sys.stderr.write("Error parsing data: exiting...")

    def parse(self):
        """
        Takes raw training data and turns it into modular sessions for manipulation

        Returns :True if it is successful, otherwise returns :False.

        """

        sessions = []
        # Make the label values a set to automatically prune duplicates
        label_vals = set() 
        # Loop over each session file in the training data, ultimately filling
        # an array with session objects for later analysis
        for filecontents in self.training_data:
            # FileContents will contain the following keys:
            # start_time, user, session_number, data
            # data['keyname'] returns the value of the key in that datapoint
            sess = self.make_session(filecontents)
            # Generate a list of features from the session, make sure they
            # are the same as any previous features we recorded for this data
            features = sess.list_features()
            if not self.featureset.check_features(features):
                sys.stderr.write("Feature set mismatch!")
                return False
            map(lambda x: label_vals.add(x), sess.get_label_keys())
            sessions.append(sess)
        # Move sessions to the class instance, set_label_vals on
        # self.featureset to have a list of possible values for your label key
        self.sessions = sessions
        self.featureset.set_label_values(list(label_vals))
        return True

    def make_session(self, data):
        """
        Instantiate a session object using raw data.  Return that object.

        :data should be the raw, unpickled dictionary of a single session
        file.

        """

        start_time = data['start_time']
        username = data['user']
        sessnum = data['session_number']
        sess_data = data['data']
        new_session = Session(sessnum, start_time, username, self.classify_on_key, sess_data)
        return new_session

