import random
import sys
import numpy

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
        self.get_points_by_label()

    def get_features(self):
        num_entries = len(self.data)
        # Choose a random data point
        entry_num = random.randint(1, num_entries) - 1
        target_entry = self.data[entry_num]
        return target_entry.keys()

    def list_features(self):
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

    def get_points_by_label(self):
        """
        Creates label_map which looks like so:
        label_map['Blue'] = [{first_point}, {second_point}]

        and feature_map which is more flexible:
        feature_map['theta'] = [{first_point}, {second_point}]
        """

        labels = list(set(self.get_label_keys()))
        label_map = {}
        feature_map = {}
        for feat in self.features:
            feature_map[feat] = []
        for item in labels:
            label_map[item] = []
        for point in self.datapoints:
            features = point.get_features()
            label_name = str()
            cleaned_output = {}
            for k,v in features:
                feature_map[k] = v
                if k != features[self.label_key]:
                    cleaned_output[k] = v
                else:
                    label_name = k
            label_map[k].append(cleaned_output)
        self.feature_map = feature_map
        self.label_map = label_map
        return label_map            


class Category(object):
    """
    Generic class to hold datapoints for each of the different categories.

    This will provide for easy operations on data in the aggregate.  It will help
    to distinguish how different colors are treated differently by the user.

    Syntax: Category(label_name, featureset)

    Methods: add_dataPoint(user, sessnum, datapoint), calculate_mean(), calculate_stdev(), 
    """

    def __init__(self, label_name, featureset):
        self.name = label_name
        self.features = featureset


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

    def __init__(self, label_key, feature_set):
        if feature_set is not None:
            self.features = feature_set
        else:
            self.features = []
        self.label_key = label_key

    def add_feature(self, feature_name):
        if feature_name not in self.features:
            self.features.append(feature_name)
        return True

    def check_features(self, data):
        session_features = data.keys()
        if len(self.features) == 0:
            self.features = session_features
        else:
            for k in session_features:
                if k not in self.features:
                    return False
        return True

    def get_label_key(self):
        return self.label_key

    def set_label_values(self, label_vals):
        self.label_values = label_vals

    def get_label_values(self):
        return self.label_values

    def get_features(self):
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
        self.username = username
        self.sessnum = sessnum
        self.data = data

    def get_feature(self, feature_name):
        return self.data[feature_name]

    def get_features(self):
        return self.data

    def get_full_data(self):
        return { 'user': self.username, 'sessnum': self.sessnum, 'data': self.data }


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
        self.featureset = Featureset(keyname)
        self.classify_on_key = keyname
        self.training_data = training_data
        # Kick off the training session with this method call
        if self.parse() is True:
            # Now we need to analyze
            self.processor = DataProcessor(self.featureset, self.sessions)
            self.processor.
        else:
            sys.stderr.write("Error parsing data: exiting...")

    def parse(self):
        sessions = []
        label_vals = set()
        for filecontents in self.training_data:
            sess = self.make_session(filecontents)
            features = sess.list_features()
            if not self.featureset.check_features(features):
                sys.stderr.write("Feature set mismatch!")
                return False
            label_vals.add(sess.get_label_keys())
            sessions.append(sess)
        self.sessions = sessions
        self.featureset.set_label_values(list(label_vals))
        return True

    def make_session(self, data):
        start_time = data['start_time']
        username = data['user']
        sessnum = data['session_number']
        sess_data = data['data']
        new_session = Session(sessnum, start_time, username, self.train_on_key, sess_data)
        return new_session


class DataProcessor(object):
    """
    This class is responsible for collecting all of the data and turning it into useful output.

    It is instantiated like:
    DataProcessor(session_list)

    and has the following methods:
    get_points_by_label([label_name]) - returns a dictionary of labels with lists of points
    get_points_by_user([user_name]) - returns a dictionary of users with lists of points
    get_points_by_session([user_name],[session_num])
        if user_name is specified alone, returns a list of sessions each with a list of points
        if user_name is specified with session_num, returns a list of points in the given session
    get_points_by_feature([feature_name]) - a list of all values for a feature if specified, or else a dict of all features
    get_mean(label=None, user=None, session=None, feature=None) -- must specify at least one
    get_stdev(label=None, user=None, session=None, feature=None) -- must specify at least one
    get_variance(label=None, user=None, session=None, feature=None)
    get_covariance_table(label=None, user=None, session=None, feature=None)
    get_median(label=None, user=None, session=None, feature=None)
    get_mode(label=None, user=None, session=None, feature=None)
    """

    # NOTE -- DEPRECATING HASH MAP GENERATION
    def __init__(self, featureset, sessions):
        self.featureset = featureset
        self.sessions = sessions
        self.datapoints = map(lambda x: x.get_data_points(), self.sessions)

    def make_point_maps(self):
        """
        Create hash maps for all of the different ways we will look at the data.
        label_map['labelName'] = [{firstpoint, secondpoint}]
        feature_map['featureName'] = ...
        user_map['username'] = ...

        May add functionality to pass a set of points through to determine new kinds of
        information e.g. all 'theta' features of user 'joe'
        """

        label_map = {}
        feature_map = {}
        user_map = {}
        full_point_list = []
        for point in self.datapoints:
            full_data = point.get_full_data() # Point dict with keys 'user', 'sessnum', and 'data'

        # add session_map to user_map in processing
        # Get all of the possible label values from the featureset
        # Label values are what we classify against, e.g. a color or an outcome to predict
        labels = self.featureset.get_label_values()
        # Set up lists for each feature key
        for feat in self.featureset.get_features():
            feature_map[feat] = []
        # Set up lists for each possible label value
        for item in labels:
            label_map[item] = []
        # Loop over all of the datapoints in this object (all datapoints in the training set)
        for point in self.datapoints:
            # Get the featureset from the datapoint
            features = point.get_features()
            full_data = point.get_full_data() # Point dictionary with keys 'user', 'sessnum', 'data'
            
            # Set this string up to hold the label value for this data point
            label_name = str()
            # Use this dictionary to store k->v pairs of labelName->[{item1}, {item2}]
            cleaned_output = {}
            for k,v in features:
                # add the data point's values for each feature to the feature map
                feature_map[k].append(v)
                if k != features[self.label_key]:
                    cleaned_output[k] = v
                else:
                    label_name = k
            label_map[label_name].append(cleaned_output)

    def get_points_by_label(self, label_name=None, point_list=None):
        """
        Returns all points in the training set with a given label
        Optionally, returns only matching points from a point selection used as a parameter.

        Returns a dictionary with label_name as the key and a list of matching points as the value
        """

        label_key = self.featureset.get_label_key()
        label_values = self.featureset.get_label_values()
        matching_points = {}
        # We are working from the full list
        if point_list == None:
            point_list = self.datapoints
        # Make the point list a list of the full data
        point_list = map(lambda x: x.get_full_data(), point_list)
        if label_name == None:
            for label in label_values:
                matching_points[label] = filter(lambda x: x['data'][label_key] == label, point_list)
        else:
            matching_points[label_name] = filter(lambda x: x['data'][label_key] == label_name, point_list)
        return matching_points

    def get_points_by_user(self, user_name=None, point_list=None):
        """
        Returns all points in the training set with a given username
        Optionallhy, returns only matching points from a list of points.

        Returns a dictionary with user_name as the key and a list of matching points as the value.
        """
        
        matching_points = {}
        if point_list == None:
            point_list = self.datapoints
        point_list = map(lambda x: x.get_full_data(), point_list)
        if user_name == None:
            for point in point_list:
                user = point['user']
                matching_points[user] = point['data']
        else:
            matching_points[user_name] = filter(lambda x: x['user'] == user_name, point_list)
        return matching_points


    def get_points_by_session(self, user_name=None, session_num=None, point_list=None):
        """
        Returns all points in the training set with a given username and session number
        Optionallhy, returns only matching points from a list of points.

        Returns a dictionary of session numbers with the values as lists of data points
        """
        
        matching_points = {}
        if session_num == None and user_name == None:
            return self.get_points_by_user(user_name=user_name, point_list=point_list)
        else if point_list == None:
            point_list = self.datapoints
        point_list = map(lambda x: x.get_full_data(), point_list)
        if session_num != None:
            matching_points[session_num] = filter(lambda x: x['sessnum'] == session_num, point_list)
        else:
            if user_name == None: return False
            else:
                user_points = filter(lambda x: x['user'] == user_name, point_list)
                for point in user_points:
                    sessnum = point['sessnum']
                    if not matching_points[sessnum]: matching_points[sessnum] = []
                    matching_points[sessnum].append(point)
        return matching_points

    def get_points_by_feature(self, feature_name=None, point_list=None):
        """
        Returns all points in the training set with a given username
        Optionallhy, returns only matching points from a list of points.

        Returns a dictionary of matching points indexed by feature_name.
        """
        
        matching_points = {}
        if point_list == None:
            point_list = self.datapoints
        point_list = map(lambda x: x.get_full_data(), point_list)
        if feature_name == None:
            for point in point_list:
                for k,v in point['data']:
                    if not matching_points[k]: matching_points[k] = []
                    matching_points[k].append(v)
        else:
            matching_points[feature_name] = map(lambda x: x['data'][feature_name], point_list)
        return matching_points

    def get_point_selection(self, label=None, user=None, session=None, feature=None, point_list=None):
        matching_points = []
        label_key = self.featureset.get_label_key()
        if point_list == None:
            point_list = self.datapoints
        point_list = map(lambda x: x.get_full_data(), point_list)
        if session is not None and not user:
            return False
        else if not label and not user and not session and not feature:
            # return all points
            matching_points = point_list
        else if not label and not user:
            # we have feature only
            matching_points = map(lambda x: x['data'][feature], point_list)
        else if not label and not session:
            # we have user and feature
            matching_points = filter(lambda y: y['user'] == user, map(lambda x: x['data'][feature], point_list))
            # matching_points[feature] = matching_points[user]
        else if not label and not feature:
            # we have user and session
            matching_points = filter(lambda x: x['user'] == user, point_list)
            matching_points = filter(lambda x: x['sessnum'] == session, matching_points)
        else if not feature and not session:
            # we have label and user
            matching_points = filter(lambda x: x['user'] == user, point_list)
            matching_points = filter(lambda x: x['data'][label_key] == label, matching_points)
        else if not user:
            # we have label and feature
            matching_points = map(lambda y: y['data'][feature], filter(lambda x: x['data'][label_key] == label, point_list))
        else if not label:
            # we have user, session and feature
            matching_points = filter(lambda y: y['sessnum'] == session, filter(lambda x: x['user'] == user, point_list))
            matching_points = map(lambda x: x['data'][feature], matching_points)
        else:
            matching_points = filter(lambda y: y['sessnum'] == session, filter(lambda x: x['user'] == user, point_list))
            matching_points = map(lambda x: x['data'][feature], matching_points)           
            matching_points = filter(lambda x: x['data'][label_key] == label, matching_points)
        return matching_points
        
    def get_mean(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)
        pass

    def get_stdev(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)

    def get_variance(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)

    def get_covariance(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)

    def get_median(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)

    def get_mode(label=None, user=None, session=None, feature=None):
        points = self.get_point_selection(label, user, session, feature)
