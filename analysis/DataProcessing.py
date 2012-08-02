import numpy

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

    def __init__(self, featureset, sessions):
        self.featureset = featureset
        self.sessions = sessions
        self.datapoints = map(lambda x: x.get_data_points(), self.sessions)

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
