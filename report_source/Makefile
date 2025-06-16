.PHONY: all watch clean

all:
	pdflatex paper.tex
	bibtex paper
	pdflatex paper.tex
	pdflatex paper.tex
	make clean
	open paper.pdf

finalsubmission:
	pdflatex paper.tex
	bibtex paper
	latexpand --expand-usepackage --expand-bbl paper.bbl --verbose paper.tex > paper_14.tex
	make clean
	mkdir -p final_submission/
	mv paper_14.tex final_submission
	sed -i "s/\.\.\/images\///g" final_submission/paper_14.tex
	cp splncs04.bst final_submission/
	cp llncs.cls final_submission/
	cp ../images/Overview2.pdf final_submission/
	cp ../images/experiment.pdf final_submission/
	cp ../images/scenario.pdf final_submission/
	cp ../images/single_run310.png final_submission/
	cp ../images/power_per_scenario_boxplot.pdf final_submission/
	cp ../images/runtime_per_scenario_boxplot.pdf final_submission/
	cp ../images/energy_per_scenario_boxplot.pdf final_submission/
	cd final_submission/; pdflatex paper_14.tex
	cd final_submission/; pdflatex paper_14.tex
	sleep 2
	rm final_submission/*.out final_submission/*.log final_submission/*.aux
	cp camera_ready/SNCS*.pdf final_submission/
	cd final_submission/; zip ../paper-14_camera_ready.zip *
# 	rm -r final_submission/
	open final_submission/paper_14.pdf

watch:
	inotifywait -m -e CLOSE_WRITE paper.tex | xargs -n1 -I{} make

clean:
	rm __latexindent_temp.tex *.aux paper.bbl paper.blg paper.fdb_latexmk paper.fls paper.log paper.out paper.ent paper.synctex.gz texput.log || true
