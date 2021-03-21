import React, {ChangeEvent, useState} from 'react';
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend} from 'recharts';
import {Container, FilterBar} from './App.style';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import Button from '@material-ui/core/Button';
import FormControl from "@material-ui/core/FormControl";
import {useAsync, useAsyncFn} from 'react-use';
import nanoid from 'nanoid';
import {InputLabel} from "@material-ui/core";

const fetchBrandsHook = async (): Promise<string[]> =>
    (await fetch(`/api/brands`)).json();

const fetchModelsHook = async (brand: string): Promise<any> =>
    (await fetch(`/api/models?brand=${brand}`)).json();

const fetchStatsHook = async (brand: string, model: string): Promise<any> =>
    (await fetch(`/api/stats?brand=${brand}&&model=${model}`)).json();

function App() {
    const [models, fetchModels] = useAsyncFn(fetchModelsHook);
    const [stats, fetchStats] = useAsyncFn(fetchStatsHook)
    const brands = useAsync(fetchBrandsHook)

    const [brand, selectBrand] = useState('')
    const [model, selectModel] = useState('')
    const handleSelectBrand = (event: ChangeEvent<{ name?: string, value: unknown }>) => {
        const selectedBrand = event.target?.value as string
        selectBrand(selectedBrand)
        fetchModels(selectedBrand)
    }

    const handleSelectModel = (event: ChangeEvent<{ name?: string, value: unknown }>) => {
        selectModel(event.target?.value as string)
    }

    const handleClick = () => {
        fetchStats(brand, model)
    }

    const data = stats.value ? Object.keys(stats.value).map(year => ({
        name: year,
        average: stats.value[year].mean as number,
        min: stats.value[year].min as number,
        max: stats.value[year].max as number,
    })) : []

    return (
        <Container>
            <FilterBar>
                <FormControl>
                    <InputLabel id="brand">Marque</InputLabel>
                    <Select labelId="brand" value={brand} onChange={handleSelectBrand}>
                        {
                            brands.value ? brands.value.map((brand: string) => <MenuItem value={brand}
                                                                                         key={nanoid()}> {brand} </MenuItem>) : null
                        }
                    </Select>
                </FormControl>

                <FormControl>
                    <InputLabel id="model">Modèle</InputLabel>
                    <Select labelId="model" value={model} onChange={handleSelectModel}>
                        {
                            models.value ? models.value.map((model: string) => <MenuItem value={model}
                                                                                         key={nanoid()}> {model} </MenuItem>) : null
                        }
                    </Select>
                </FormControl>

                <Button onClick={handleClick}>
                    Recherche
                </Button>
            </FilterBar>

            {
                data.length > 0 &&
                <LineChart
                    width={500}
                    height={300}
                    data={data}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3"/>
                    <XAxis dataKey="name"/>
                    <YAxis/>
                    <Tooltip/>
                    <Legend/>
                    <Line type="monotone" dataKey="average" stroke="#edb42d"/>
                    <Line type="monotone" dataKey="min" stroke="#339c16"/>
                    <Line type="monotone" dataKey="max" stroke="#ff0000"/>

                </LineChart>
            }

        </Container>
    );
}

export default App;
