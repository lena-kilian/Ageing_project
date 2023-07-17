# UKMRIO 2023

This code contains the 2023 version of the UKMRIO model (in 'code' folder).

## Script order

1. ukmrio_main_2023.py
2. LCF_data_main_2023.py
3. defra_main_2023.py

Functions used

| Script used | Function script | Function name | Date updated |
| :---: | :---: | :---: | :---: |
| ukmrio_main_2023.py | co2_stressor_functions | make_co2_382 | 13/02/2023 |
| ukmrio_main_2023.py | co2_stressor_functions | make_exio382_stressor | 13/02/2023 |
| ukmrio_main_2023.py | co2_stressor_functions | make_ghg_382 | 13/02/2023 |
| ukmrio_main_2023.py | co2_stressor_functions | make_old_exio_stressor_382 | 13/02/2023 |
| ukmrio_main_2023.py | co2_stressor_functions | make_UK_emissions | 13/02/2023 |
| defra_main_2023.py | demand_functions | make_Yhh_109_34 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | demand_functions | make_Yhh_109_34 | 13/02/2023 |
| generations_2023_main.py | demand_functions | make_Yhh_109_34 | 13/02/2023 |
| defra_main_2023.py | defra_functions | makeukresults2023 | 13/02/2023 |
| defra_main_2023.py | defra_functions | printdefradata | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | defra_functions | makeukresults2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | defra_functions | makeregionresults2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | defra_functions | printdefradata | 13/02/2023 |
| generations_2023_main.py | defra_functions | makeukresults2023 | 13/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | lacheck | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | makelaresults2023 | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | makeregionresults2023 | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | makeukresults2023 | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | printdefradata | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | printdefradata2 | 23/02/2023 |
| sub_national_footprints_2023_main.py | defra_functions | regioncheck2023 | 23/02/2023 |
| defra_main_2023.py | LCF_functions | convert43to41 | 13/02/2023 |
| defra_main_2023.py | LCF_functions | convert_exp_tot_sizes | 13/02/2023 |
| defra_main_2023.py | LCF_functions | convert_hhspend_sizes | 13/02/2023 |
| defra_main_2023.py | LCF_functions | make_balanced_totals_2023 | 13/02/2023 |
| defra_main_2023.py | LCF_functions | make_new_Y_109 | 13/02/2023 |
| defra_main_2023.py | LCF_functions | make_totals_2023 | 13/02/2023 |
| defra_main_2023.py | LCF_functions | make_y_hh_109 | 13/02/2023 |
| defra_main_2023.py | LCF_functions | make_y_regions_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | convert43to41 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | convert_exp_tot_sizes | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | convert_hhspend_sizes | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_balanced_totals_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_new_Y_109 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_totals_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_y_countries_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_y_hh_109 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | make_y_regions_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | LCF_functions | removeoutliers | 13/02/2023 |
| generations_2023_main.py | LCF_functions | convert43to41 | 13/02/2023 |
| generations_2023_main.py | LCF_functions | convert_exp_tot_sizes | 13/02/2023 |
| generations_2023_main.py | LCF_functions | convert_hhspend_sizes | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhagecohortfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhagefoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhincfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhinc2foots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhoacfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhregfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | make_balanced_totals_2023 | 13/02/2023 |
| generations_2023_main.py | LCF_functions | make_new_Y_109 | 13/02/2023 |
| generations_2023_main.py | LCF_functions | make_totals_2023 | 13/02/2023 |
| generations_2023_main.py | LCF_functions | make_y_hh_109 | 13/02/2023 |
| generations_2023_main.py | LCF_functions | processdataforfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhagefoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popagefoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhincfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popincfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhinc2foots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popinc2foots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhregfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popregfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhoacfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popoacfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | hhagecohortfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | popagecohortfoots | 13/02/2023 |
| generations_2023_main.py | LCF_functions | removeoutliers | 13/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | add_pop_factors | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | convert43to41 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | convert_exp_tot_sizes | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | convert_hhspend_sizes | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | correct_la_spend_props_gas_elec_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | correct_reglaspendyr_zero | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | hhagefoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | hhincfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | hhinc2foots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | hhoacfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | hhregfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_balanced_totals_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_la_spend_props_by_region_year | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_la_spends_pop_by_region_year_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_new_Y_109 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_pop_hhold_by_oac_region_year_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_totals_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_y_countries_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_y_hh_109 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_y_regional | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | make_y_regions_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | makeoacspends_2023 | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | popagefoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | popincfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | popinc2foots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | popoacfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | popregfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | processdataforfoots | 14/02/2023 |
| sub_national_footprints_2023_main.py | LCF_functions | removeoutliers | 14/02/2023 |
| ukmrio_main_2023.py | mat_stressor_functions | make_exio_stressor_382 | 13/02/2023 |
| ukmrio_main_2023.py | mat_stressor_functions | make_mat | 13/02/2023 |
| ukmrio_main_2023.py | mat_stressor_functions | make_UK_exioMAT | 13/02/2023 |
| ukmrio_main_2023.py | mat_stressor_functions | make_uk_stressor | 13/02/2023 |
| ukmrio_main_2023.py | metadata | make_meta | 13/02/2023 |
| ukmrio_main_2023.py | nrg_stressor_functions | iea_to_full_exio382 | 13/02/2023 |
| ukmrio_main_2023.py | nrg_stressor_functions | make_IEA_data | 13/02/2023 |
| ukmrio_main_2023.py | nrg_stressor_functions | make_nrg_2023 | 13/02/2023 |
| ukmrio_main_2023.py | nrg_stressor_functions | uk_exio_nrg | 13/02/2023 |
| ukmrio_main_2023.py | ons | align_analytic_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | align_old_SUT_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | combine_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | combine_fd | 02/02/2023 |
| ukmrio_main_2023.py | ons | combine_fd_hh | 02/02/2023 |
| ukmrio_main_2023.py | ons | load_hh_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | load_io_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | load_old_io_data | 02/02/2023 |
| ukmrio_main_2023.py | ons | make_hh_prop | 02/02/2023 |
| ukmrio_main_2023.py | ons | make_old_fd_coicop | 02/02/2023 |
| ukmrio_main_2023.py | ons | make_wide_Y | 02/02/2023 |
| ukmrio_main_2023.py | ons | remove_fd_negatives | 02/02/2023 |
| defra_main_2023.py | ukmrio_functions | deflate_io_regions | 13/02/2023 |
| defra_main_2023.py | ukmrio_functions | get_deflator_data_2023 | 13/02/2023 |
| defra_main_2023.py | ukmrio_functions | make_v | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | ukmrio_functions | deflate_io_regions | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | ukmrio_functions | get_deflator_data_2023 | 13/02/2023 |
| defra_uk_devolved_regions_2023.py | ukmrio_functions | make_v | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | apply_ras50 | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | balancer_prep | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | combine_exio | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | convert_to_gbp | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | correctY | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | footprint | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | get_exiobase382 | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | make_domprop | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | make_exio_props | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | make_old_exio | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | split_tables | 13/02/2023 |
| ukmrio_main_2023.py | ukmrio_functions | split_y | 13/02/2023 |
| ukmrio_main_2023.py | wat_stressor_functions | make_exio382_wat |  |


## License

This project is licensed under the [MIT License](LICENSE)
