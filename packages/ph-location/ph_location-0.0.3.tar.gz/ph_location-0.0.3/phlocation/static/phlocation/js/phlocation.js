window.addEventListener('load', (event) => {
    const regionSelect = document.querySelector('select.ph-location.region');
    const provinceSelect = document.querySelector('select.ph-location.district-province');
    const municipalitySelect = document.querySelector('select.ph-location.city-municipality');
    const barangaySelect = document.querySelector('select.ph-location.barangay');

    regionSelect.innerHTML = '';
    provinceSelect.innerHTML = '';
    municipalitySelect.innerHTML = '';
    barangaySelect.innerHTML = '';

    const loadingOption = document.createElement('option');
    loadingOption.value = '';
    loadingOption.textContent = 'Loading...';

    const selectRegionOption = document.createElement('option');
    selectRegionOption.value = '';
    selectRegionOption.textContent = 'Select a region first.';

    const selectProvinceOption = document.createElement('option');
    selectProvinceOption.value = '';
    selectProvinceOption.textContent = 'Select a province first.';

    const selectMunicipalityOption = document.createElement('option');
    selectMunicipalityOption.value = '';
    selectMunicipalityOption.textContent = 'Select a city/municipality first.';

    regionSelect.append(loadingOption);
    provinceSelect.append(selectRegionOption);
    municipalitySelect.append(selectProvinceOption);
    barangaySelect.append(selectMunicipalityOption);

    function setOptions(select, defaultOption, items, defaultValueCallback = () => {}) {
        select.innerHTML = '';
        defaultOption.textContent = '------';
        select.append(defaultOption);

        const selectDefaultValue = select.getAttribute('data-value');

        items.forEach(item => {
            const option = document.createElement('option');

            option.value = item.code;
            option.textContent = item.name;

            select.append(option);
        });

        select.value = selectDefaultValue;
        defaultValueCallback({target: select});
    }

    function initializeRegionSelect() {
        fetch('/api/phlocation/')
            .then(response => response.json())
            .then(regions => setOptions(regionSelect, loadingOption, regions, handleRegionChange));
    }

    function handleRegionChange(event) {
        if (!event.target.value) {
            return setOptions(provinceSelect, selectRegionOption, [], handleProvinceChange);
        }
        fetch(`/api/phlocation/${event.target.value}/`)
            .then(response => response.json())
            .then(provinces => setOptions(provinceSelect, selectRegionOption, provinces, handleProvinceChange))
    }

    function handleProvinceChange(event) {
        if (!event.target.value) {
            return setOptions(municipalitySelect, selectProvinceOption, []);
        }
        fetch(`/api/phlocation/${regionSelect.value}/${event.target.value}/`)
            .then(response => response.json())
            .then(municipalities => setOptions(
                municipalitySelect,
                selectProvinceOption,
                municipalities,
                handleMunicipalityChange
            ))
    }

    function handleMunicipalityChange(event) {
        if (!event.target.value) {
            return setOptions(barangaySelect, selectMunicipalityOption, []);
        }
        fetch(`/api/phlocation/${regionSelect.value}/${provinceSelect.value}/${event.target.value}/`)
            .then(response => response.json())
            .then(barangays => setOptions(
                barangaySelect,
                selectMunicipalityOption,
                barangays,
            ))
    }

    initializeRegionSelect();

    regionSelect.addEventListener('change', handleRegionChange, false);
    provinceSelect.addEventListener('change', handleProvinceChange, false);
    municipalitySelect.addEventListener('change', handleMunicipalityChange, false);
});
