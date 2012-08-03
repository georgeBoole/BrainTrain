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
        expanded_points = []
        for session_points in point_list:
            map(lambda x: expanded_points.append(x.get_full_data()), session_points)
        point_list = expanded_points
#       point_list = map(lambda x: x.get_full_data(), point_list)
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
        expanded_points = []
        for session_points in point_list:
            map(lambda x: expanded_points.append(x.get_full_data()), session_points)
        point_list = expanded_points
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
        elif point_list == None:
            point_list = self.datapoints
        expanded_points = []
        for session_points in point_list:
            map(lambda x: expanded_points.append(x.get_full_data()), session_points)
        point_list = expanded_points
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
        expanded_points = []
        for session_points in point_list:
            map(lambda x: expanded_points.append(x.get_full_data()), session_points)
        point_list = expanded_points
        if feature_name == None:
            for point in point_list:
                for k,v in point['data']:
                    if not matching_points[k]: matching_points[k] = []
                    matching_points[k].append(v)
        else:
            matching_points[feature_name] = map(lambda x: x['data'][feature_name], point_list)
        return matching_points

    def get_point_selection(self, label=None, user=None, session_number=None, feature=None):
        matching_points = []
        label_key = self.featureset.get_label_key()
        point_list = self.datapoints
        expanded_points = []
        for session_points in point_list:
            map(lambda x: expanded_points.append(x), session_points)
        point_list = expanded_points
        if label:
            point_list = filter(lambda x: x.get_feature(label_key) == label, point_list)
        if user:
            point_list = filter(lambda x: x.get_user() == user, point_list)
            if session_number:
                point_list = filter(lambda x: x.get_sessnum() == session_number, point_list)
        if feature:
            point_list = { 
                    feature : map(lambda x: x.get_feature(feature), point_list),
                    }
#       matching_points = map(lambda x: x.get_full_data(), point_list)
#       return matching_points
        return point_list

    def get_mean(self, label=None, user=None, session_number=None, feature=None):
        points = self.get_point_selection(label=label, user=user, 
                session_number=session_number, feature=feature)
        output = {}
        for key, val in points.iteritems():
            output[key] = numpy.mean(numpy.array(val))
        return output

    def get_stdev(self, label=None, user=None, session_number=None, feature=None):
        points = self.get_point_selection(label=label, user=user, 
                session_number=session_number, feature=feature)
        output = {}
        for key, val in points.iteritems():
            output[key] = numpy.std(numpy.array(val))
        return output

    def get_variance(self, label=None, user=None, session_number=None, feature=None):
        points = self.get_point_selection(label=label, user=user, 
                session_number=session_number, feature=feature)
        output = {}
        for key, val in points.iteritems():
            output[key] = numpy.array(val).var()
        return output
        # you can use pointarray.var(axis=0 or 1) for column and row variance

#    def get_covariance(label=None, user=None, session=None, feature=None):
#        points = self.get_point_selection(label, user, session, feature)

    def get_median(self, label=None, user=None, session_number=None, feature=None):
        points = self.get_point_selection(label=label, user=user, 
                session_number=session_number, feature=feature)
        output = {}
        for key, val in points.iteritems():
            output[key] = numpy.median(numpy.array(val))
        return output

    def get_mode(self, label=None, user=None, session_number=None, feature=None):
        points = self.get_point_selection(label=label, user=user, 
                session_number=session_number, feature=feature)
        output = {}
        for key, val in points.iteritems():
            output[key] = numpy.mean(numpy.array(val))
        return output
