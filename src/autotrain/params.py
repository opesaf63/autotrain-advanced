from dataclasses import dataclass

from autotrain.languages import SUPPORTED_LANGUAGES
from autotrain.tasks import TASKS


class LoraR:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 100
    DEFAULT = 16
    STEP = 1
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "LoRA R"


class LoraAlpha:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 256
    DEFAULT = 32
    STEP = 1
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "LoRA Alpha"


class LoraDropout:
    TYPE = "float"
    MIN_VALUE = 0.0
    MAX_VALUE = 1.0
    DEFAULT = 0.05
    STEP = 0.01
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "LoRA Dropout"


class LearningRate:
    TYPE = "float"
    MIN_VALUE = 1e-7
    MAX_VALUE = 1e-1
    DEFAULT = 1e-3
    STEP = 1e-6
    FORMAT = "%.2E"
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Learning Rate"


class LMLearningRate(LearningRate):
    DEFAULT = 5e-5


class Optimizer:
    TYPE = "str"
    DEFAULT = "adamw_torch"
    CHOICES = ["adamw_torch", "adamw_hf", "sgd", "adafactor", "adagrad"]
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Optimizer"


class LMTrainingType:
    TYPE = "str"
    DEFAULT = "generic"
    CHOICES = ["generic", "chat"]
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "LM Training Type"


class Scheduler:
    TYPE = "str"
    DEFAULT = "linear"
    CHOICES = ["linear", "cosine"]
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Scheduler"


class TrainBatchSize:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 128
    DEFAULT = 2
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Train Batch Size"


class LMTrainBatchSize(TrainBatchSize):
    DEFAULT = 4


class Epochs:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 1000
    DEFAULT = 10
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Epochs"


class LMEpochs(Epochs):
    DEFAULT = 1


class PercentageWarmup:
    TYPE = "float"
    MIN_VALUE = 0.0
    MAX_VALUE = 1.0
    DEFAULT = 0.1
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Percentage Warmup"


class GradientAccumulationSteps:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 100
    DEFAULT = 1
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Gradient Accumulation Steps"


class WeightDecay:
    TYPE = "float"
    MIN_VALUE = 0.0
    MAX_VALUE = 1.0
    DEFAULT = 0.0
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Weight Decay"


class SourceLanguage:
    TYPE = "str"
    DEFAULT = "en"
    CHOICES = SUPPORTED_LANGUAGES
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Source Language"


class TargetLanguage:
    TYPE = "str"
    DEFAULT = "en"
    CHOICES = SUPPORTED_LANGUAGES
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Target Language"


class NumModels:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 25
    DEFAULT = 1
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Number of Models"


class DBNumSteps:
    TYPE = "int"
    MIN_VALUE = 100
    MAX_VALUE = 10000
    DEFAULT = 1500
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Number of Steps"


class DBTextEncoderStepsPercentage:
    TYPE = "int"
    MIN_VALUE = 1
    MAX_VALUE = 100
    DEFAULT = 30
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Text encoder steps percentage"


class DBPriorPreservation:
    TYPE = "bool"
    DEFAULT = False
    STREAMLIT_INPUT = "checkbox"
    PRETTY_NAME = "Prior preservation"


class ImageSize:
    TYPE = "int"
    MIN_VALUE = 64
    MAX_VALUE = 2048
    DEFAULT = 512
    STREAMLIT_INPUT = "number_input"
    PRETTY_NAME = "Image Size"


class DreamboothConceptType:
    TYPE = "str"
    DEFAULT = "person"
    CHOICES = ["person", "object"]
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Concept Type"


class SourceLanguageUnk:
    TYPE = "str"
    DEFAULT = "unk"
    CHOICES = ["unk"]
    STREAMLIT_INPUT = "selectbox"
    PRETTY_NAME = "Source Language"


@dataclass
class Params:
    task: str
    param_choice: str
    model_choice: str

    def __post_init__(self):
        # task should be one of the keys in TASKS
        if self.task not in TASKS:
            raise ValueError(f"task must be one of {TASKS.keys()}")
        self.task_id = TASKS[self.task]

        if self.param_choice not in ("autotrain", "manual"):
            raise ValueError("param_choice must be either autotrain or manual")

        if self.model_choice not in ("autotrain", "hub_model"):
            raise ValueError("model_choice must be either autotrain or hub_model")

    def _dreambooth(self):
        if self.param_choice == "manual":
            return {
                "image_size": ImageSize,
                "learning_rate": LearningRate,
                "train_batch_size": TrainBatchSize,
                "num_steps": DBNumSteps,
                "text_encoder_steps_percentage": DBTextEncoderStepsPercentage,
                "prior_preservation": DBPriorPreservation,
            }
        if self.param_choice == "autotrain":
            if self.model_choice == "hub_model":
                return {
                    "image_size": ImageSize,
                    "num_models": NumModels,
                }
            else:
                return {
                    "num_models": NumModels,
                }

    def _tabular_binary_classification(self):
        return {
            "num_models": NumModels,
        }

    def _lm_training(self):
        if self.param_choice == "manual":
            return {
                "learning_rate": LMLearningRate,
                "optimizer": Optimizer,
                "scheduler": Scheduler,
                "train_batch_size": LMTrainBatchSize,
                "num_train_epochs": LMEpochs,
                "percentage_warmup": PercentageWarmup,
                "gradient_accumulation_steps": GradientAccumulationSteps,
                "weight_decay": WeightDecay,
                "lora_r": LoraR,
                "lora_alpha": LoraAlpha,
                "lora_dropout": LoraDropout,
                "training_type": LMTrainingType,
            }
        if self.param_choice == "autotrain":
            return {
                "num_models": NumModels,
                "training_type": LMTrainingType,
            }
        raise ValueError("param_choice must be either autotrain or manual")

    def _tabular_multi_class_classification(self):
        return self._tabular_binary_classification()

    def _tabular_single_column_regression(self):
        return self._tabular_binary_classification()

    def tabular_multi_label_classification(self):
        return self._tabular_binary_classification()

    def _text_binary_classification(self):
        if self.param_choice == "manual":
            return {
                "learning_rate": LearningRate,
                "optimizer": Optimizer,
                "scheduler": Scheduler,
                "train_batch_size": TrainBatchSize,
                "num_train_epochs": Epochs,
                "percentage_warmup": PercentageWarmup,
                "gradient_accumulation_steps": GradientAccumulationSteps,
                "weight_decay": WeightDecay,
            }
        if self.param_choice == "autotrain":
            if self.model_choice == "autotrain":
                return {
                    "source_language": SourceLanguage,
                    "num_models": NumModels,
                }
            return {
                "source_language": SourceLanguageUnk,
                "num_models": NumModels,
            }
        raise ValueError("param_choice must be either autotrain or manual")

    def _text_multi_class_classification(self):
        return self._text_binary_classification()

    def _text_entity_extraction(self):
        return self._text_binary_classification()

    def _text_single_column_regression(self):
        return self._text_binary_classification()

    def _text_natural_language_inference(self):
        return self._text_binary_classification()

    def _image_binary_classification(self):
        if self.param_choice == "manual":
            return {
                "learning_rate": LearningRate,
                "optimizer": Optimizer,
                "scheduler": Scheduler,
                "train_batch_size": TrainBatchSize,
                "num_train_epochs": Epochs,
                "percentage_warmup": PercentageWarmup,
                "gradient_accumulation_steps": GradientAccumulationSteps,
                "weight_decay": WeightDecay,
            }
        return {
            "num_models": NumModels,
        }

    def _image_multi_class_classification(self):
        return self._image_binary_classification()

    def get(self):
        if self.task in ("text_binary_classification", "text_multi_class_classification"):
            return self._text_binary_classification()

        if self.task == "text_entity_extraction":
            return self._text_entity_extraction()

        if self.task == "text_single_column_regression":
            return self._text_single_column_regression()

        if self.task == "text_natural_language_inference":
            return self._text_natural_language_inference()

        if self.task == "tabular_binary_classification":
            return self._tabular_binary_classification()

        if self.task == "tabular_multi_class_classification":
            return self._tabular_multi_class_classification()

        if self.task == "tabular_single_column_regression":
            return self._tabular_single_column_regression()

        if self.task == "tabular_multi_label_classification":
            return self.tabular_multi_label_classification()

        if self.task in ("image_binary_classification", "image_multi_class_classification"):
            return self._image_binary_classification()

        if self.task == "dreambooth":
            return self._dreambooth()

        if self.task == "lm_training":
            return self._lm_training()

        raise ValueError(f"task {self.task} not supported")
