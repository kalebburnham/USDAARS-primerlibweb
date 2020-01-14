"""
License information goes here.
"""

from flask_wtf import FlaskForm
from wtforms import (TextAreaField, FloatField, BooleanField, IntegerField,
                     SubmitField, StringField)
#from wtforms import validators
from wtforms.validators import (InputRequired, Length, ValidationError,
                                NumberRange)

from nestedloop import (TEMPERATURE_MIN, TEMPERATURE_MAX,
                        NUM_TO_RETURN_MIN, PCR_MINIMUM, PCR_MAXIMUM,
                        REF_SEQ_MIN_LENGTH, REF_SEQ_MAX_LENGTH, F_FROM_MIN,
                        F_TO_MIN, R_FROM_MIN, R_TO_MIN)

class StarpForm(FlaskForm):
    input_data = TextAreaField(
        label='input_data',
        validators=[InputRequired(),
                    Length(min=50,
                           max=20000,
                           message='input_data must be between 50 and 20,000 characters.')]
    )
    submit = SubmitField('Submit')

# DEFAULTS
NUM_TO_RETURN_DEFAULT = 5
PCR_MIN_DEFAULT = 3000
PCR_MAX_DEFAULT = 8000
TM_MIN_DEFAULT = 54.0
TM_OPT_DEFAULT = 56.0
TM_MAX_DEFAULT = 58.0
F_FROM_DEFAULT = 1
F_TO_DEFAULT = 1
R_FROM_DEFAULT = 1
R_TO_DEFAULT = 1

class ValidateTemperature:
    def __init__(
            self,
            min=TEMPERATURE_MIN,
            max=TEMPERATURE_MAX,
            message=(f'Temperature must be between {str(TEMPERATURE_MIN)} '
                     f'and {str(TEMPERATURE_MAX)} degrees.')
        ):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        tm = field.data
        # Data is None if its of the wrong type.
        if tm is None:
            return

        if tm < self.min or tm > self.max:
            raise ValidationError(self.message)

class ValidateReferenceSequence:
    def __init__(
            self,
            min=REF_SEQ_MIN_LENGTH,
            max=REF_SEQ_MAX_LENGTH,
            message=f'Reference sequence must be between {str(REF_SEQ_MIN_LENGTH)}'
                    f' and {str(REF_SEQ_MAX_LENGTH)} characters.'
        ):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        """ It's ok if this field is empty as long as both primers
        are entered. """

        if form.forward_primer.data and form.reverse_primer.data:
            print(form.forward_primer)
            return

        seq = field.data
        if len(seq) < self.min or len(seq) > self.max:
            raise ValidationError(self.message)

class NestedLoopForm(FlaskForm):
    ref_sequence = TextAreaField(
        label='Reference Sequence for NL-PCR Primer Design',
        validators=[ValidateReferenceSequence()],
        render_kw={'maxlength': REF_SEQ_MAX_LENGTH}
    )

    non_targets = TextAreaField(label='Non-specific alignments')

    specificity_checking = BooleanField(label='Specificity Checking')

    f_from = IntegerField(
        label='Region for forward primer:',
        validators=[InputRequired(),
                    NumberRange(min=F_FROM_MIN,
                                message="Regions must be positive numbers.")],
        default=F_FROM_DEFAULT,
        render_kw={'type': 'number',
                   'min': F_FROM_MIN,
                   'required': 'true'}
    )

    f_to = IntegerField(
        label='To',
        validators=[InputRequired(),
                    NumberRange(min=F_TO_MIN,
                                message="Regions must be positive numbers.")],
        default=F_TO_DEFAULT,
        render_kw={'type': 'number',
                   'min': F_TO_MIN,
                   'required': 'true'}
    )

    r_from = IntegerField(
        label='Region for reverse primer:',
        validators=[InputRequired(),
                    NumberRange(min=R_FROM_MIN,
                                message="Regions must be positive numbers.")],
        default=R_FROM_DEFAULT,
        render_kw={'type': 'number',
                   'min': R_FROM_MIN,
                   'required': 'true'}
    )

    r_to = IntegerField(
        label='To',
        validators=[InputRequired(),
                    NumberRange(min=R_TO_MIN,
                                message="Regions must be positive numbers.")],
        default=R_TO_DEFAULT,
        render_kw={'type': 'number',
                   'min': R_TO_MIN,
                   'required': 'true'}
    )

    tm_min = FloatField(
        label='Tm Min',
        validators=[InputRequired(), ValidateTemperature()],
        default=TM_MIN_DEFAULT,
        render_kw={'type': 'number',
                   'step': 'any',
                   'min': TEMPERATURE_MIN,
                   'max': TEMPERATURE_MAX,
                   'required': 'true'}
    )

    tm_opt = FloatField(
        label='Tm Opt',
        validators=[InputRequired(), ValidateTemperature()],
        default=TM_OPT_DEFAULT,
        render_kw={'type': 'number',
                   'step': 'any',
                   'min': TEMPERATURE_MIN,
                   'max': TEMPERATURE_MAX,
                   'required': 'true'}
    )

    tm_max = FloatField(
        label='Tm Max',
        validators=[InputRequired(), ValidateTemperature()],
        default=TM_MAX_DEFAULT,
        render_kw={'type': 'number',
                   'step': 'any',
                   'min': TEMPERATURE_MIN,
                   'max': TEMPERATURE_MAX,
                   'required': 'true'}
    )

    num_to_return = IntegerField(
        label='Number to Return',
        validators=[InputRequired(),
                    NumberRange(min=NUM_TO_RETURN_MIN,
                                message=f'Must return at least {str(NUM_TO_RETURN_MIN)} primers!')],
        default=NUM_TO_RETURN_DEFAULT,
        render_kw={'type': 'number',
                   'min': NUM_TO_RETURN_MIN,
                   'required': 'true'}
    )

    pcr_min = IntegerField(
        label='PCR Min',
        default=PCR_MIN_DEFAULT,
        render_kw={'type': 'number',
                   'min': PCR_MINIMUM,
                   'max': PCR_MAXIMUM,
                   'required': 'true'}
    )

    pcr_max = IntegerField(
        label='PCR Max',
        default=PCR_MAX_DEFAULT,
        render_kw={'type': 'number',
                   'min': PCR_MINIMUM,
                   'max': PCR_MAXIMUM,
                   'required': 'true'}
    )

    forward_primer = StringField(label='Forward Primer')
    reverse_primer = StringField(label='Reverse Primer')
    submit = SubmitField(label='Find Primers')
    nested_loop_error = None
