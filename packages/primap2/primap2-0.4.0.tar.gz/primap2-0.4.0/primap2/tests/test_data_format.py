#!/usr/bin/env python
"""Tests for _data_format.py"""
import logging

import pandas as pd
import pint
import pytest
import xarray as xr

import primap2

from .utils import assert_ds_aligned_equal


def test_something_else_entirely(caplog):
    with pytest.raises(ValueError, match=r"ds is not an xr.Dataset"):
        something_else = primap2._data_format.DatasetDataFormatAccessor(ds="asdf")
        something_else.ensure_valid()
    assert "ERROR" in caplog.text
    assert "object is not an xarray Dataset." in caplog.text


def test_valid_ds_pass(any_ds, caplog):
    caplog.set_level(logging.INFO)
    any_ds.pr.ensure_valid()
    assert not caplog.records


def test_io_roundtrip(any_ds: xr.Dataset, caplog, tmp_path):
    ds = any_ds
    caplog.set_level(logging.INFO)
    ds.pr.to_netcdf(tmp_path / "temp.nc")
    nds = primap2.open_dataset(tmp_path / "temp.nc")
    nds.pr.ensure_valid()
    assert not caplog.records
    xr.testing.assert_identical(ds, nds)
    assert_ds_aligned_equal(ds, nds)


def test_required_dimension_missing(caplog):
    ds = xr.Dataset(
        {
            "area (ISO3)": ["a"],
            "time": pd.date_range("2000-01-01", "2020-01-01", freq="AS"),
        },
        attrs={"area": "area (ISO3)"},
    ).pr.quantify()

    with pytest.raises(ValueError, match=r"'source' not in dims"):
        ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'source' not found in dims, but is required." in caplog.text


def test_required_coordinate_missing(minimal_ds, caplog):
    del minimal_ds["source"]
    with pytest.raises(ValueError, match=r"dim 'source' has no coord"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "No coord found for dimension 'source'." in caplog.text


def test_dimension_metadata_missing(minimal_ds, caplog):
    del minimal_ds.attrs["area"]
    with pytest.raises(ValueError, match=r"'area' not in attrs"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert (
        "'area' not found in attrs, required dimension is therefore undefined."
        in caplog.text
    )


def test_dimension_metadata_wrong(minimal_ds, caplog):
    minimal_ds.attrs["area"] = "asdf"
    with pytest.raises(ValueError, match=r"'area' dimension not in dims"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'asdf' defined as 'area' dimension, but not found in dims." in caplog.text


def test_wrong_provenance_value(opulent_ds, caplog):
    opulent_ds["provenance"] = ["asdf"]
    with pytest.raises(ValueError, match=r"Invalid provenance: \{'asdf'\}"):
        opulent_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "provenance contains invalid values: {'asdf'}" in caplog.text


def test_additional_dimension(minimal_ds: xr.Dataset, caplog):
    ds = minimal_ds.expand_dims({"addl_dim": ["a", "b", "c"]})  # type: ignore
    ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert (
        "Dimension(s) {'addl_dim'} unknown, likely a typo or missing in sec_cats."
        in caplog.text
    )


def test_wrong_dimension_key(minimal_ds, caplog):
    ds = minimal_ds.rename_dims({"area (ISO3)": "asdf"})
    ds.attrs["area"] = "asdf"
    with pytest.raises(
        ValueError, match=r"'asdf' not in the format 'dim \(category_set\)'"
    ):
        ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'asdf' not in the format 'dim (category_set)'." in caplog.text


def test_missing_sec_cat(minimal_ds, caplog):
    minimal_ds.attrs["sec_cats"] = ["missing"]
    with pytest.raises(ValueError, match="Secondary category 'missing' not in dims"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "Secondary category 'missing' defined, but not found in dims." in caplog.text


def test_missing_optional_dim(minimal_ds, caplog):
    minimal_ds.attrs["scen"] = "missing"
    with pytest.raises(ValueError, match="'scen' not in dims"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'missing' defined as scen, but not found in dims." in caplog.text


def test_sec_cat_without_primary_cat(minimal_ds, caplog):
    ds = minimal_ds.expand_dims({"something (cset)": ["a", "b", "c"]})
    ds.attrs["sec_cats"] = ["something (cset)"]
    ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert (
        "Secondary category defined, but no primary category defined, weird."
        in caplog.text
    )


def test_additional_coordinate_space(opulent_ds: xr.Dataset, caplog):
    ds = opulent_ds.rename({"category_names": "category names"})
    with pytest.raises(
        ValueError, match=r"Coord key 'category names' contains a space"
    ):
        ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert (
        "Additional coordinate name 'category names' contains a space,"
        " replace it with an underscore." in caplog.text
    )


def test_missing_entity(minimal_ds, caplog):
    del minimal_ds["CO2"].attrs["entity"]
    with pytest.raises(ValueError, match="entity missing for 'CO2'"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'CO2' has no entity declared in attributes." in caplog.text


def test_weird_entity(minimal_ds, caplog):
    minimal_ds["CO2"].attrs["entity"] = "carbondioxide"
    minimal_ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert "entity 'carbondioxide' of 'CO2' is unknown." in caplog.text


def test_missing_gwp_context(minimal_ds, caplog):
    del minimal_ds["SF6 (SARGWP100)"].attrs["gwp_context"]
    minimal_ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert (
        "'SF6 (SARGWP100)' has the dimension [CO2 * mass / time], but is not CO2. "
        "gwp_context missing?" in caplog.text
    )


def test_wrong_units(minimal_ds, caplog):
    deq = minimal_ds.pint.dequantify()
    deq["CO2"].attrs["units"] = "kg CO2"
    req = deq.pr.quantify()
    req.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert (
        "'CO2' has a unit of CO2 * kilogram, which is not compatible with an emission "
        "rate." in caplog.text
    )


def test_unquantified(minimal_ds, caplog):
    deq = minimal_ds.pint.dequantify()
    deq.pr.ensure_valid()
    assert not caplog.records


def test_multi_units(minimal_ds, caplog):
    minimal_ds["CO2"].attrs["units"] = "kg CO2 / year"
    with pytest.raises(ValueError, match="data already has units"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'units' in variable attrs, but data is quantified already." in caplog.text


def test_invalid_units(minimal_ds, caplog):
    deq = minimal_ds.pint.dequantify()
    deq["CO2"].attrs["units"] = "i_am_not_a_unit"
    with pytest.raises(pint.UndefinedUnitError):
        deq.pr.ensure_valid()


def test_invalid_gwp_context(minimal_ds, caplog):
    minimal_ds["SF6 (SARGWP100)"].attrs["gwp_context"] = "i_am_not_a_gwp_context"
    with pytest.raises(
        ValueError,
        match=r"Invalid gwp_context 'i_am_not_a_gwp_context' for 'SF6 \(SARGWP100\)'",
    ):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert (
        "gwp_context 'i_am_not_a_gwp_context' for 'SF6 (SARGWP100)' is not valid."
        in caplog.text
    )


def test_extraneous_gwp_context(minimal_ds, caplog):
    minimal_ds["SF6"].attrs["gwp_context"] = "SARGWP100"
    with pytest.raises(
        ValueError, match=r"SF6 has wrong dimensionality for gwp_context."
    ):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert (
        "'SF6' is a global warming potential, but the dimension is not "
        "[CO2 * mass / time]." in caplog.text
    )


def test_missing_unit(minimal_ds, caplog):
    minimal_ds["CO2"] = (minimal_ds["CO2"].dims, minimal_ds["CO2"].pint.magnitude)
    minimal_ds["CO2"].attrs["entity"] = "CO2"
    with pytest.raises(ValueError, match=r"units missing for 'CO2'"):
        minimal_ds.pr.ensure_valid()
    assert "ERROR" in caplog.text
    assert "'CO2' has no units." in caplog.text


def test_weird_variable_name(minimal_ds, caplog):
    caplog.set_level(logging.INFO)
    minimal_ds["weird_name"] = minimal_ds["CO2"]
    minimal_ds["weird_name"].attrs["entity"] = "CO2"
    minimal_ds.pr.ensure_valid()
    assert "INFO" in caplog.text
    assert "The name 'weird_name' is not in standard format 'CO2'." in caplog.text


def test_missing_gwp_in_variable_name(minimal_ds, caplog):
    minimal_ds["SF6_gwp"] = minimal_ds["SF6 (SARGWP100)"]
    minimal_ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert "'SF6_gwp' has a gwp_context in attrs, but not in its name." in caplog.text


def test_weird_contact(minimal_ds, caplog):
    caplog.set_level(logging.INFO)
    minimal_ds.attrs["contact"] = "i_am_not_an_email"
    minimal_ds.pr.ensure_valid()
    assert "INFO" in caplog.text
    assert "Contact information is not an email address" in caplog.text


def test_weird_references(minimal_ds, caplog):
    caplog.set_level(logging.INFO)
    minimal_ds.attrs["references"] = "i_am_not_a_doi"
    minimal_ds.pr.ensure_valid()
    assert "INFO" in caplog.text
    assert "Reference information is not a DOI" in caplog.text


def test_nonstandard_attribute(minimal_ds, caplog):
    minimal_ds.attrs["i_am_not_standard"] = ""
    minimal_ds.pr.ensure_valid()
    assert "WARNING" in caplog.text
    assert "Unknown metadata in attrs: {'i_am_not_standard'}, typo?" in caplog.text
