import locale

from rest_framework import serializers
from tasks.models import Telescope, Point, Task, TrackPoint, Frame, TrackingData, TLEData, BalanceRequest
from tasks.helpers import converting_degrees, is_float, is_int


class TelescopeSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        deg, min, sec = converting_degrees(obj.latitude)
        place = 'N' if obj.latitude > 0 else 'S'
        return f'{deg}°{min}\'{sec}\" {place}'

    def get_longitude(self, obj):
        deg, min, sec = converting_degrees(obj.longitude)
        place = 'E' if obj.longitude > 0 else 'W'
        return f'{deg}°{min}\'{sec}\" {place}'

    def get_status(self, obj):
        return obj.get_status_display()

    def get_balance(self, obj):
        return obj.get_user_balance(self.context['request'].user)

    class Meta:
        model = Telescope
        fields = ('id', 'name', 'avatar', 'status', 'description', 'location', 'latitude', 'longitude', 'balance')


class TelescopeBalanceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='name')
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        return obj.get_user_balance(self.context['request'].user)

    class Meta:
        model = Telescope
        fields = ('label', 'value', 'balance')


class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = ('alpha', 'beta', 'cs_type', 'dt', 'exposure', 'mag', 'satellite_id')


class TrackingDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrackingData
        fields = ('satellite_id', 'mag', 'step_sec', 'count')


class TleDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TLEData
        fields = ('satellite_id', 'line1', 'line2')


class TrackPointSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrackPoint
        fields = ('alpha', 'beta', 'dt')


class FrameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Frame
        fields = ('exposure', 'dt')


class PointTaskSerializer(serializers.ModelSerializer):
    telescope = serializers.CharField(source='telescope.id')
    points = PointSerializer(many=True)
    duration = serializers.FloatField()
    min_dt = serializers.DateTimeField()
    max_dt = serializers.DateTimeField()

    class Meta:
        model = Task
        fields = ('telescope', 'points', 'duration', 'min_dt', 'max_dt')

    def validate_points(self, points):
        if not points:
            raise serializers.ValidationError('В задании должна быть выбрана хотя бы одна точка для наблюдения')
        for point in points:
            satellite_id = point.get('satellite_id')
            mag = point.get('mag')
            alpha = point.get('alpha')
            beta = point.get('beta')
            exposure = point.get('exposure')
            cs_type = point.get('cs_type')
            dt = point.get('dt')
            errors = []
            if not is_int(satellite_id) or satellite_id < 0:
                errors.append('введен некорректный ID спутника')
            if not is_int(mag) or mag < 0:
                errors.append('введена некорректная звездная величина')
            if not is_int(exposure) or exposure < 0:
                errors.append('введена некорректная выдержка')
            if cs_type not in [Point.EARTH_SYSTEM, Point.STARS_SYSTEM]:
                errors.append('неправильно указана система координат')
            if not is_float(alpha) or alpha < 0 or alpha > 360:
                errors.append('введен некорректный азимут')
            if not is_float(beta) or beta < 0 or beta > 90:
                errors.append('введена некорректная высота')
            if errors:
                raise serializers.ValidationError(f'Найдены следующие ошибки: {", ".join(errors)}')

    def save_points(self, instance, points):
        nested_serializer = PointSerializer(data=points, many=True)
        nested_serializer.is_valid(raise_exception=True)
        points_list = nested_serializer.save()
        for point in points_list:
            point.task_id = instance.id
            point.save()
        return instance

    def create(self, validated_data):
        telescope_id = validated_data.pop('telescope').get('id')
        points = self.context['request'].data.get('points')
        min_dt = self.context['request'].data.get('min_dt')
        max_dt = self.context['request'].data.get('max_dt')
        user = self.context['request'].user
        self.validate_points(points)
        instance = Task.objects.create(author=user, task_type=Task.POINTS_MODE, telescope_id=telescope_id)
        instance.start_dt = min_dt
        instance.end_dt = max_dt
        self.save_points(instance, points)
        instance.save()
        return instance


class TrackingTaskSerializer(serializers.ModelSerializer):
    telescope = serializers.CharField(source='telescope.id')
    tracking_data = TrackingDataSerializer()
    track_points = TrackPointSerializer(many=True)
    frames = FrameSerializer(many=True)
    duration = serializers.FloatField()
    min_dt = serializers.DateTimeField()
    max_dt = serializers.DateTimeField()

    class Meta:
        model = Task
        fields = ('telescope', 'tracking_data', 'track_points', 'frames', 'duration', 'min_dt', 'max_dt')

    def validate_tracking_task(self, tracking_data):
        satellite_id = tracking_data.get('satellite_id')
        mag = tracking_data.get('mag')
        step_sec = tracking_data.get('step_sec')
        errors = []
        if not is_int(satellite_id) or satellite_id < 0:
            errors.append('введен некорректный ID спутника')
        if not is_int(mag) or mag < 0:
            errors.append('введена некорректная звездная величина')
        if not is_int(step_sec) or step_sec < 0:
            errors.append('введен некорректный временной шаг')
        if errors:
            raise serializers.ValidationError(f'Найдены следующие ошибки: {", ".join(errors)}')

    def validate_track(self, track_points):
        if len(track_points) < 2:
            raise serializers.ValidationError('В задании должны быть выбраны хотя бы две точки для перемещения')
        for point in track_points:
            alpha = point.get('alpha')
            beta = point.get('beta')
            errors = []
            if not is_float(alpha) or alpha < 0 or alpha > 360:
                errors.append('введен некорректный азимут')
            if not is_float(beta) or beta < 0 or beta > 90:
                errors.append('введена некорректная высота')
            if errors:
                raise serializers.ValidationError(f'Найдены следующие ошибки: {", ".join(errors)}')

    def validate_frames(self, frames):
        if not frames:
            raise serializers.ValidationError('В задании должны быть выбран хотя бы один момент для съемки')
        for frame in frames:
            exposure = frame.get('exposure')
            if not is_int(exposure) or exposure < 0:
                raise serializers.ValidationError('Введена некорректная выдержка')

    def save_tracking_data(self, instance, tracking_data):
        nested_serializer = TrackingDataSerializer(data=tracking_data)
        nested_serializer.is_valid(raise_exception=True)
        tracking_data_obj = nested_serializer.save()
        tracking_data_obj.task_id = instance.id
        tracking_data_obj.save()
        return tracking_data_obj

    def save_track(self, instance, track_data):
        nested_serializer = TrackPointSerializer(data=track_data, many=True)
        nested_serializer.is_valid(raise_exception=True)
        track_list = nested_serializer.save()
        for track in track_list:
            track.task_id = instance.id
            track.save()
        return track_list

    def save_frames(self, instance, frames_data):
        nested_serializer = FrameSerializer(data=frames_data, many=True)
        nested_serializer.is_valid(raise_exception=True)
        frames_list = nested_serializer.save()
        for frame in frames_list:
            frame.task_id = instance.id
            frame.save()
        return frames_list

    def create(self, validated_data):
        telescope_id = validated_data.pop('telescope').get('id')
        tracking_data = self.context['request'].data.get('tracking_data')
        track = self.context['request'].data.get('track_points')
        frames = self.context['request'].data.get('frames')
        min_dt = self.context['request'].data.get('min_dt')
        max_dt = self.context['request'].data.get('max_dt')
        user = self.context['request'].user
        self.validate_tracking_task(tracking_data)
        self.validate_track(track)
        self.validate_frames(frames)
        instance = Task.objects.create(author=user, task_type=Task.TRACKING_MODE, telescope_id=telescope_id)
        instance.start_dt = min_dt
        instance.end_dt = max_dt
        self.save_tracking_data(instance, tracking_data)
        self.save_track(instance, track)
        self.save_frames(instance, frames)
        instance.save()
        return instance


class TleTaskSerializer(serializers.ModelSerializer):
    telescope = serializers.CharField(source='telescope.id')
    tle_data = TleDataSerializer()
    frames = FrameSerializer(many=True)
    duration = serializers.FloatField()
    min_dt = serializers.DateTimeField()
    max_dt = serializers.DateTimeField()

    class Meta:
        model = Task
        fields = ('telescope', 'tle_data', 'frames', 'duration', 'min_dt', 'max_dt')

    def save_tle_data(self, instance, tle_data):
        nested_serializer = TleDataSerializer(data=tle_data)
        nested_serializer.is_valid(raise_exception=True)
        tle_data_obj = nested_serializer.save()
        tle_data_obj.task_id = instance.id
        tle_data_obj.save()
        return tle_data_obj

    def save_frames(self, instance, frames_data):
        nested_serializer = FrameSerializer(data=frames_data, many=True)
        nested_serializer.is_valid(raise_exception=True)
        frames_list = nested_serializer.save()
        for frame in frames_list:
            frame.task_id = instance.id
            frame.save()
        return frames_list

    def validate_frames(self, frames):
        if not frames:
            raise serializers.ValidationError('В задании должны быть выбран хотя бы один момент для съемки')
        for frame in frames:
            exposure = frame.get('exposure')
            if not is_int(exposure) or exposure < 0:
                raise serializers.ValidationError('Введена некорректная выдержка')

    def create(self, validated_data):
        telescope_id = validated_data.pop('telescope').get('id')
        tle_data = self.context['request'].data.get('tle_data')
        frames = self.context['request'].data.get('frames')
        min_dt = self.context['request'].data.get('min_dt')
        max_dt = self.context['request'].data.get('max_dt')
        user = self.context['request'].user
        self.validate_frames(frames)
        if not is_int(tle_data.get('satellite_id')) or tle_data.get('satellite_id') < 0:
            raise serializers.ValidationError('Введен некорректный ID спутника')
        instance = Task.objects.create(author=user, task_type=Task.TLE_MODE, telescope_id=telescope_id)
        self.save_tle_data(instance, tle_data)
        self.save_frames(instance, frames)
        instance.start_dt = min_dt
        instance.end_dt = max_dt
        instance.save()
        return instance


class BalanceRequestSerializer(serializers.ModelSerializer):
    telescope = serializers.CharField(source='telescope.name')
    created = serializers.SerializerMethodField()
    approved = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_created(self, obj):
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        return obj.created_at.strftime('%d %b %Y, %H:%M')

    def get_approved(self, obj):
        return obj.approved_by.get_full_name() if obj.approved_by else ''

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = BalanceRequest
        fields = ('telescope', 'minutes', 'status', 'created', 'approved')


class BalanceRequestCreateSerializer(serializers.ModelSerializer):
    telescope = serializers.CharField(source='telescope.id')
    minutes = serializers.IntegerField()

    class Meta:
        model = BalanceRequest
        fields = ('telescope', 'minutes')

    def create(self, validated_data):
        telescope_id = validated_data.pop('telescope').get('id')
        minutes = validated_data.pop('minutes')
        user = self.context['request'].user
        instance = BalanceRequest.objects.create(user=user, minutes=minutes, telescope_id=telescope_id)
        return instance
