from django.contrib.admin.decorators import register
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import site

from silk.profiling.profiler import silk_profile

from .models import \
    DataSchema, \
    JSONDataSet, NamedJSONDataSet, \
    NumPyArray, NamedNumPyArray, \
    PandasDataFrame, NamedPandasDataFrame, \
    CSVDataSet, NamedCSVDataSet, \
    ParquetDataSet, NamedParquetDataSet, \
    TFRecordDataSet, NamedTFRecordDataSet


@register(DataSchema, site=site)
class DataSchemaAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {DataSchema._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(name=f'{__module__}: {DataSchema._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(JSONDataSet, site=site)
class JSONDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {JSONDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {JSONDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedJSONDataSet, site=site)
class NamedJSONDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {NamedJSONDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedJSONDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NumPyArray, site=site)
class NumPyArrayAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {NumPyArray._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NumPyArray._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedNumPyArray, site=site)
class NamedNumPyArrayAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {NamedNumPyArray._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedNumPyArray._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(PandasDataFrame, site=site)
class PandasDataFrameAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(name=f'{__module__}: {PandasDataFrame._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {PandasDataFrame._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedPandasDataFrame, site=site)
class NamedPandasDataFrameAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {NamedPandasDataFrame._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedPandasDataFrame._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(CSVDataSet, site=site)
class CSVDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {CSVDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {CSVDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedCSVDataSet, site=site)
class NamedCSVDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {NamedCSVDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedCSVDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(ParquetDataSet, site=site)
class ParquetDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {ParquetDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {ParquetDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedParquetDataSet, site=site)
class NamedParquetDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {NamedParquetDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedParquetDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(TFRecordDataSet, site=site)
class TFRecordDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {TFRecordDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {TFRecordDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)


@register(NamedTFRecordDataSet, site=site)
class NamedTFRecordDataSetAdmin(ModelAdmin):
    show_full_result_count = False

    @silk_profile(
        name=f'{__module__}: {NamedTFRecordDataSet._meta.verbose_name}')
    def changeform_view(self, *args, **kwargs):
        return super().changeform_view(*args, **kwargs)

    @silk_profile(
        name=f'{__module__}: {NamedTFRecordDataSet._meta.verbose_name_plural}')
    def changelist_view(self, *args, **kwargs):
        return super().changelist_view(*args, **kwargs)
