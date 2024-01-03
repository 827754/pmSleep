async function getPokemonEvolutionChain  (pokemonId, recordIndex, mode) {
    var index = app.vueFormData.findIndex(({ index }) => index === recordIndex);
    // 進化表示
    if (mode == "disp") {
        if (app.vueFormData[index]['evolution'].length != 0) {
            app.$set(app.vueFormData[index], 'displayEvolutionArea', true)
            app.vueFormData.push(null)
            app.vueFormData.pop()
            return
        }
    } else {
        if (app.vueFormData[index]['evolution'].length != 0) {
            app.evolutionFilter.splice(0)
            app.evolutionFilter = [...app.vueFormData[index]['evolution']]
            return
        }

    }
    if (app.vueFormData[index]['evolutionLoad'] == true) {
        return
    }
    app.$set(app.vueFormData[index], 'evolutionLoad', true)
    app.vueFormData.push(null)
    app.vueFormData.pop()

    const speciesURL = `https://pokeapi.co/api/v2/pokemon-species/${pokemonId}/`;
    var speciesList = []
    await fetch(speciesURL)
        .then(response => {
            if (!response.ok) {
                throw new Error('データの取得に失敗しました');
            }
            return response.json();
        })
        .then(data => {
            const evolutionChainURL = data['evolution_chain']['url'];
            return fetch(evolutionChainURL);
        })
        .then(evolutionResponse => {
            if (!evolutionResponse.ok) {
                throw new Error('進化情報の取得に失敗しました');
            }
            return evolutionResponse.json();
        })
        .then(evolutionData => {
            speciesList = app.extractSpecies(evolutionData['chain']);
        })
        .catch(error => {
            console.error(error.message);
        });

    // console.log(speciesList); // 抽出された species データのリストを出力
    const idsArray = speciesList.map(item => {
        const id = item.url.split('/').filter(str => str !== '').pop();
        return parseInt(id);
    });


    var varieties = []
    var varietiesObjs = []

    for (const e of idsArray) {

        const varietiesURL = `https://pokeapi.co/api/v2/pokemon-species/${e}/`;
        await fetch(varietiesURL)
            .then(response => {
                if (!response.ok) {
                    throw new Error('データの取得に失敗しました');
                }
                return response.json();
            })
            .then(data => {
                const tmp = data['varieties'];
                const namesJa = data.names.filter(item => item.language.name === "ja").map(item => item.name);
                // console.log(namesJa);
                varietiesConcat = tmp.map(variety => {
                    const urlParts = variety.pokemon.url.split('/');
                    return parseInt(urlParts[urlParts.length - 2]);
                });
                // console.log(varietiesConcat)
                tmpObj = {}
                tmpObj['name'] = namesJa[0]
                tmpObj['IDs'] = []

                varietiesConcat.forEach(id => {
                    tmpObj["IDs"].push({ "id": String(id), "name": id == e ? namesJa[0] : "" });
                });

                varieties.push(...varietiesConcat)
                varietiesObjs.push(tmpObj)
            })
            .catch(error => {
                console.error(error.message);
            });

    }

    for (let pokemon of varietiesObjs) {
        for (let entry of pokemon.IDs) {
            if (entry.name === "") {
                const formURL = `https://pokeapi.co/api/v2/pokemon/${entry.id}/`;
                // console.log(formURL)
                entry.name = await fetch(formURL)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('データの取得に失敗しました');
                        }
                        return response.json();
                    })
                    .then(data => {
                        const formsURL = data.forms[0].url;
                        // console.log(formsURL)
                        return fetch(formsURL);
                    })
                    .then(formResponse => {
                        if (!formResponse.ok) {
                            throw new Error('進化情報の取得に失敗しました');
                        }
                        return formResponse.json();
                    })
                    .then(formData => {
                        // console.log(formData)
                        const namesJa = formData.form_names.filter(item => item.language.name === "ja").map(item => item.name);

                        if (namesJa == '') {
                            const namesEn = formData.form_names.filter(item => item.language.name === "en").map(item => item.name);
                            if (namesEn == '') {
                                return pokemon.name
                            }
                            return pokemon.name + ":" + namesEn[0]
                        }
                        // console.log(namesJa);
                        return pokemon.name + ":" + namesJa[0]
                    })
                    .catch(error => {
                        console.error(error.message);
                    });
            }
        }
    }
    var newIDs = [];

    for (const entry of varietiesObjs) {
        newIDs.push(...entry.IDs);
    }

    app.vueFormData[index]['evolution'].splice(0)
    app.$set(app.vueFormData[index], 'evolution', [...newIDs])
    app.$set(app.vueFormData[index], 'evolutionLoad', false)

    if (mode == "disp") {
        app.$set(app.vueFormData[index], 'displayEvolutionArea', true)

    } else {
        app.evolutionFilter.splice(0)
        app.evolutionFilter = [...app.vueFormData[index]['evolution']]
        app.$set(app.vueFormData[index], 'displayEvolutionArea', false)
    }
    app.vueFormData.push(null)
    app.vueFormData.pop()

}