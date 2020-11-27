#pr3-1
select co1.name from country as co1
cross join country co2 
cross join 
(
	select * from country order by country.gnp desc limit 1
)co3
cross join 
(
	select * from country where country.population > 0
	order by country.surfacearea / country.population desc limit 1
) co4
where co2.name = 'Argentina' and co1.population > 0 and co1.name <> 'Argentina'
order by 
abs(co1.gnp/co3.gnp + (co1.surfacearea/co1.population)/(co4.surfacearea/co4.population) - 
co2.gnp/co3.gnp - (co2.surfacearea/co2.population)/(co4.surfacearea/co4.population)) 
limit 10;

#pr3
select 'GLE' as "Indicator", co1.lifeexpectancy as "Federal Republic", co2.lifeexpectancy as "Republic", co3.lifeexpectancy as "Others"
from country col
cross join 
(
	select* from country where country.governmentform = 'Republic'
	order by country.lifeexpectancy desc limit 1 
) co2 
cross join 
(
	select* from country where country.governmentform <> 'Republic' and
	country.governmentform <> 'Federal Republic' and country.lifeexpectancy is not null order by country.lifeexpectancy desc limit 1
) co3
where co1.governmentform = 'Federal Republic'
order by co1.lifeexpectancy desc limit 1)
union distinct 
(
	select 'LLE' as "Indicator", co1.lifeexpectancy as "Federal Republic", co2.lifeexpectancy as "Republic", co3.lifeexpectancy as "Others"
from country co1
cross join 
(
	select* from country where country.governmentform = 'Republic'
	order by country.lifeexpectancy asc limit 1 
) co2 
cross join 
(
	select* from country where country.governmentform <> 'Republic' and
	country.governmentform <> 'Federal Republic' order by country.lifeexpectancy asc limit 1
) co3
where co1.governmentform = 'Federal Republic'
order by co1.lifeexpectancy asc limit 1
)

#pr 4-1
select ct.* from city as ct
left join country on country.capital = ct.id
where country.capital is NULL and ct.population >= 8000000;

select c.name countryname,  ct.name cityname,  ct.population as city_population
from city as ct 
join country as c on c.code = ct.countrycode 
join (select avg(population) as ave, countrycode from city group by countrycode) ct1 on ct1.countrycode = ct.countrycode 
where ct.population > ct1.ave
order by c.name, ct.name;
